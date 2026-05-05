from __future__ import annotations

import json
import urllib.parse
import urllib.request

from neurocartographer.models import DatasetCandidate, QuerySpec


class DandiConnector:
    """Tiny DANDI REST connector with conservative parsing and no credentials."""

    name = "dandi"

    def __init__(self, api_base: str = "https://api.dandiarchive.org/api") -> None:
        self.api_base = api_base.rstrip("/")

    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]:
        if limit <= 0:
            return []
        term = query.search_terms[0] if query.search_terms else query.original_question
        params = urllib.parse.urlencode({"search": term, "page_size": str(min(max(limit * 5, limit), 50))})
        url = f"{self.api_base}/dandisets/?{params}"
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "neurocartographer/0.1"})
        with urllib.request.urlopen(request, timeout=15) as response:  # nosec B310 - fixed HTTPS default, user-overridable for tests
            payload = json.loads(response.read().decode("utf-8"))
        return [_candidate_from_dandi(item) for item in _results(payload)]


def _results(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return [item for item in payload["results"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _candidate_from_dandi(item: dict[str, object]) -> DatasetCandidate:
    identifier = str(item.get("identifier") or item.get("id") or "unknown")
    version = _preferred_version(item)
    title = _first_text(item.get("name"), item.get("title"), version.get("name"), f"DANDI {identifier}")
    description = _first_text(
        item.get("description"),
        version.get("description"),
        "No description returned by DANDI metadata search.",
    )
    url = _first_text(item.get("url"), version.get("url"), f"https://dandiarchive.org/dandiset/{identifier}")
    asset_count = _first_int(item.get("asset_count"), item.get("assets_count"), version.get("asset_count"))
    text = f"{title} {description} {json.dumps(version, sort_keys=True)}".lower()
    modalities = _detect_modalities(text)
    species = _detect_species(text)
    regions = _detect_regions(text)
    metadata: dict[str, object] = {"standard": "NWB", "access": "open", "verification": "dandi_api_metadata"}
    if asset_count is not None:
        metadata["asset_count"] = asset_count
    return DatasetCandidate(
        identifier=f"DANDI:{identifier}" if not identifier.startswith("DANDI:") else identifier,
        title=title,
        source="DANDI",
        url=url,
        description=description,
        species=tuple(species),
        brain_regions=tuple(regions),
        modalities=tuple(modalities),
        keywords=(),
        assets=(),
        metadata=metadata,
    )


def _preferred_version(item: dict[str, object]) -> dict[str, object]:
    for key in ("draft_version", "most_recent_published_version", "version"):
        value = item.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _first_int(*values: object) -> int | None:
    for value in values:
        if isinstance(value, int):
            return value
    return None


def _detect_species(text: str) -> list[str]:
    species: list[str] = []
    if "mouse" in text or "mice" in text:
        species.append("mouse")
    if "human" in text or "participant" in text or "subject" in text:
        species.append("human")
    if "rat" in text:
        species.append("rat")
    return species


def _detect_regions(text: str) -> list[str]:
    regions: list[str] = []
    if "visual" in text or "v1" in text:
        regions.append("visual cortex")
    if "hippoc" in text or "ca1" in text:
        regions.append("hippocampus")
    if "motor" in text:
        regions.append("motor cortex")
    return regions


def _detect_modalities(text: str) -> list[str]:
    modalities: list[str] = []
    if "calcium" in text or "ophys" in text or "two-photon" in text:
        modalities.append("calcium imaging")
    if "electrophysiology" in text or "neuropixels" in text or "spike" in text or "ecephys" in text:
        modalities.append("extracellular electrophysiology")
    if "eeg" in text:
        modalities.append("EEG")
    if "fmri" in text or "bold" in text:
        modalities.append("fMRI")
    if "behavior" in text or "behaviour" in text or "locomotion" in text:
        modalities.append("behavior")
    return modalities
