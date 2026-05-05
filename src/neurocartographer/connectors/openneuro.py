from __future__ import annotations

import json
import urllib.request

from neurocartographer.models import DatasetCandidate, QuerySpec

_GRAPHQL_URL = "https://openneuro.org/crn/graphql"


class OpenNeuroConnector:
    """Read-only OpenNeuro/BIDS connector using the public GraphQL API."""

    name = "openneuro"

    def __init__(self, graphql_url: str = _GRAPHQL_URL) -> None:
        self.graphql_url = graphql_url

    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]:
        if limit <= 0:
            return []
        payload = {
            "query": _ADVANCED_SEARCH_QUERY,
            "variables": {
                "query": _search_input(query),
                "first": max(1, min(limit, 5)),
            },
        }
        response_payload = self._post(payload, timeout=12)
        candidates = parse_openneuro_payload(response_payload)
        if candidates:
            return candidates
        fallback_payload = {
            "query": _DATASETS_QUERY,
            "variables": {
                "first": max(1, min(limit, 5)),
                "modality": _openneuro_modality(query),
            },
        }
        return parse_openneuro_payload(self._post(fallback_payload, timeout=12))

    def _post(self, payload: dict[str, object], timeout: int) -> object:
        request = urllib.request.Request(
            self.graphql_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "neurocartographer/0.2",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310 - fixed HTTPS endpoint by default
            return json.loads(response.read().decode("utf-8"))


_ADVANCED_SEARCH_QUERY = """
query NeuroCartographerOpenNeuroSearch($query: DatasetSearchInput!, $first: Int) {
  advancedSearch(query: $query, allDatasets: true, datasetStatus: "public", first: $first) {
    edges {
      node {
        id
        name
        public
        metadata {
          datasetName
          species
          modalities
          studyDomain
          trialCount
        }
        latestSnapshot {
          tag
          description {
            Name
            DatasetType
          }
        }
      }
    }
  }
}
"""

_DATASETS_QUERY = """
query NeuroCartographerOpenNeuroDatasets($first: Int, $modality: String) {
  datasets(first: $first, modality: $modality, filterBy: {public: true}) {
    edges {
      node {
        id
        name
        public
        metadata {
          datasetName
          species
          modalities
          studyDomain
          trialCount
        }
        latestSnapshot {
          tag
          description {
            Name
            DatasetType
          }
        }
      }
    }
  }
}
"""


def parse_openneuro_payload(payload: object) -> list[DatasetCandidate]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    containers = [data.get("advancedSearch"), data.get("datasets"), data.get("search")]
    candidates: list[DatasetCandidate] = []
    for container in containers:
        if not isinstance(container, dict):
            continue
        for edge in container.get("edges") or []:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node")
            if isinstance(node, dict):
                candidates.append(_candidate_from_node(node))
    return candidates


def _candidate_from_node(node: dict[str, object]) -> DatasetCandidate:
    dataset_id = str(node.get("id") or "unknown")
    metadata = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
    snapshot = node.get("latestSnapshot") if isinstance(node.get("latestSnapshot"), dict) else {}
    description = snapshot.get("description") if isinstance(snapshot.get("description"), dict) else {}
    title = _first_text(node.get("name"), metadata.get("datasetName"), description.get("Name"), dataset_id)
    files = _files(snapshot)
    modalities = _normalise_modalities(metadata.get("modalities"))
    species = _normalise_species(metadata.get("species"))
    text = " ".join([title, str(metadata.get("studyDomain") or ""), " ".join(modalities)]).lower()
    keywords = tuple(token for token in ("resting state", "task", "clinical") if token in text)
    assets = tuple(_format_asset_name(file) for file in files)
    asset_preview_source = "openneuro_graphql_file_preview" if assets else "default_bids_patterns"
    if not assets:
        assets = _default_bids_assets(modalities)
    candidate_metadata: dict[str, object] = {
        "standard": "BIDS",
        "access": "open" if node.get("public") else "unknown",
        "verification": "openneuro_graphql_metadata",
        "snapshot_tag": snapshot.get("tag"),
        "study_domain": metadata.get("studyDomain"),
        "trial_count": metadata.get("trialCount"),
        "asset_preview": files,
        "asset_preview_source": asset_preview_source,
    }
    return DatasetCandidate(
        identifier=f"OpenNeuro:{dataset_id}",
        title=title,
        source="OpenNeuro",
        url=f"https://openneuro.org/datasets/{dataset_id}",
        description=_description(title, metadata, description),
        species=species,
        brain_regions=(),
        modalities=modalities,
        keywords=keywords,
        assets=assets,
        metadata=candidate_metadata,
    )


def _search_input(query: QuerySpec) -> dict[str, object]:
    payload: dict[str, object] = {"publicOnly": True}
    keywords = _keywords(query)
    if keywords:
        payload["keywords"] = keywords
    modality = _openneuro_modality(query)
    if modality:
        payload["modality"] = modality
    if query.species:
        payload["species"] = query.species[0].title()
    return payload


def _keywords(query: QuerySpec) -> list[str]:
    values = [*query.species, *query.brain_regions, *query.keywords]
    for modality in query.modalities:
        if modality not in {"EEG", "MEG", "fMRI", "behavior"}:
            values.append(modality)
    return [value for value in dict.fromkeys(values) if value]


def _openneuro_modality(query: QuerySpec) -> str | None:
    for modality in query.modalities:
        if modality == "EEG":
            return "eeg"
        if modality == "MEG":
            return "meg"
        if modality == "fMRI":
            return "mri"
    return None


def _files(snapshot: dict[str, object]) -> list[dict[str, object]]:
    raw = snapshot.get("files")
    if not isinstance(raw, list):
        return []
    return [file for file in raw if isinstance(file, dict)]


def _format_asset_name(file: dict[str, object]) -> str:
    filename = str(file.get("filename") or "unknown")
    return filename.rstrip("/") + "/" if file.get("directory") else filename


def _default_bids_assets(modalities: tuple[str, ...]) -> tuple[str, ...]:
    assets = ["dataset_description.json", "participants.tsv"]
    if "EEG" in modalities:
        assets.append("sub-*/eeg/*_eeg.*")
    elif "MEG" in modalities:
        assets.append("sub-*/meg/*_meg.*")
    elif "fMRI" in modalities:
        assets.append("sub-*/func/*_bold.nii.gz")
    else:
        assets.append("sub-*/")
    return tuple(assets)


def _description(title: str, metadata: dict[str, object], description: dict[str, object]) -> str:
    pieces = [title]
    for key in ("studyDomain", "species"):
        value = metadata.get(key)
        if value:
            pieces.append(str(value))
    dtype = description.get("DatasetType")
    if dtype:
        pieces.append(f"dataset type {dtype}")
    return "; ".join(pieces)


def _normalise_species(value: object) -> tuple[str, ...]:
    text = str(value or "").lower()
    if not text:
        return ()
    if "human" in text or "homo sapiens" in text:
        return ("human",)
    if "mouse" in text or "mus musculus" in text:
        return ("mouse",)
    if "rat" in text:
        return ("rat",)
    return (text,)


def _normalise_modalities(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [str(item) for item in value]
    else:
        values = []
    result: list[str] = []
    for item in values:
        lower = item.lower()
        if lower == "eeg" or "eeg" in lower:
            result.append("EEG")
        elif lower == "meg" or "meg" in lower:
            result.append("MEG")
        elif lower in {"mri", "fmri"} or "bold" in lower:
            result.append("fMRI")
        elif lower:
            result.append(item)
    return tuple(dict.fromkeys(result))


def _first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""
