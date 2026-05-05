from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neurocartographer.artifacts import write_artifacts
from neurocartographer.connectors.dandi import DandiConnector
from neurocartographer.connectors.openneuro import OpenNeuroConnector
from neurocartographer.connectors.static_catalog import StaticCatalogConnector
from neurocartographer.inspection import summarize_assets
from neurocartographer.models import AssetInfo, DatasetCandidate, DatasetInspection, NotebookExecutionReport, RankedCandidate
from neurocartographer.modalities import modality_hint_from_path
from neurocartographer.query import parse_question
from neurocartographer.ranking import rank_candidates


@dataclass(frozen=True)
class PipelineResult:
    question: str
    output_dir: Path
    ranked_candidates: tuple[RankedCandidate, ...]
    artifact_paths: tuple[Path, ...]
    inspections: tuple[DatasetInspection, ...] = ()
    execution_report: NotebookExecutionReport | None = None


def run_pipeline(
    question: str,
    output_dir: Path | str,
    offline: bool = False,
    limit: int = 5,
    execute_notebook: bool = False,
) -> PipelineResult:
    if not question.strip():
        raise ValueError("question must not be empty")
    if limit <= 0:
        raise ValueError("limit must be positive")

    output_path = Path(output_dir)
    query = parse_question(question)
    candidates = _collect_candidates(query, offline=offline, limit=limit)
    ranked = rank_candidates(query, candidates)[:limit]
    inspections = tuple(_inspect_candidate(item.candidate, offline=offline) for item in ranked)
    artifacts, execution_report = write_artifacts(
        question,
        query,
        ranked,
        inspections,
        output_path,
        offline=offline,
        execute_notebook=execute_notebook,
    )
    return PipelineResult(
        question=question,
        output_dir=output_path,
        ranked_candidates=tuple(ranked),
        artifact_paths=tuple(artifacts),
        inspections=inspections,
        execution_report=execution_report,
    )


def _collect_candidates(query, offline: bool, limit: int) -> list[DatasetCandidate]:
    if offline:
        return StaticCatalogConnector().search(query, limit=limit)

    candidates: list[DatasetCandidate] = []
    for connector in (DandiConnector(), OpenNeuroConnector()):
        try:
            candidates.extend(connector.search(query, limit=limit))
        except Exception:
            # Public open-data APIs are best-effort. Falling back preserves local
            # artifact generation while provenance marks the metadata source.
            continue
    if candidates:
        return candidates
    return StaticCatalogConnector().search(query, limit=limit)


def _inspect_candidate(candidate: DatasetCandidate, offline: bool) -> DatasetInspection:
    assets = _candidate_assets(candidate)
    if not offline and candidate.source == "DANDI" and candidate.identifier.startswith("DANDI:"):
        try:
            live_assets = DandiConnector().inspect_assets(candidate, limit=25)
            if live_assets:
                assets = live_assets
        except Exception:
            # Keep the seed/metadata asset preview when live inspection is down.
            pass
    return summarize_assets(candidate, assets)


def _candidate_assets(candidate: DatasetCandidate) -> tuple[AssetInfo, ...]:
    asset_preview = candidate.metadata.get("asset_preview")
    if isinstance(asset_preview, list):
        parsed = tuple(_asset_from_preview(item) for item in asset_preview if isinstance(item, dict))
        if parsed:
            return parsed
    default_metadata = {"source": "default_bids_pattern"} if candidate.metadata.get("asset_preview_source") == "default_bids_patterns" else None
    return tuple(_asset_from_path(path, metadata=default_metadata) for path in candidate.assets)


def _asset_from_preview(item: dict[str, object]) -> AssetInfo:
    filename = str(item.get("filename") or item.get("path") or "unknown")
    if item.get("directory"):
        filename = filename.rstrip("/") + "/"
    size = item.get("size") if isinstance(item.get("size"), int) else None
    return _asset_from_path(filename, size_bytes=size, metadata={"annexed": item.get("annexed"), "directory": item.get("directory")})


def _asset_from_path(path: str, size_bytes: int | None = None, metadata: dict[str, object] | None = None) -> AssetInfo:
    lower = path.lower()
    standard = "NWB" if lower.endswith(".nwb") or "*.nwb" in lower else "BIDS" if _looks_like_bids(path) else "unknown"
    return AssetInfo(path=path, size_bytes=size_bytes, standard=standard, modality_hint=modality_hint_from_path(lower), metadata=metadata or {})


def _looks_like_bids(path: str) -> bool:
    lower = path.lower().rstrip("/")
    return lower == "dataset_description.json" or lower == "participants.tsv" or lower.startswith("sub-") or "/sub-" in lower
