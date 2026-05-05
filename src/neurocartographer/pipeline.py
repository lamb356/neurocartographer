from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neurocartographer.artifacts import write_artifacts
from neurocartographer.connectors.dandi import DandiConnector
from neurocartographer.connectors.static_catalog import StaticCatalogConnector
from neurocartographer.models import DatasetCandidate, RankedCandidate
from neurocartographer.query import parse_question
from neurocartographer.ranking import rank_candidates


@dataclass(frozen=True)
class PipelineResult:
    question: str
    output_dir: Path
    ranked_candidates: tuple[RankedCandidate, ...]
    artifact_paths: tuple[Path, ...]


def run_pipeline(question: str, output_dir: Path | str, offline: bool = False, limit: int = 5) -> PipelineResult:
    if not question.strip():
        raise ValueError("question must not be empty")
    if limit <= 0:
        raise ValueError("limit must be positive")

    output_path = Path(output_dir)
    query = parse_question(question)
    candidates = _collect_candidates(query, offline=offline, limit=limit)
    ranked = rank_candidates(query, candidates)[:limit]
    artifacts = write_artifacts(question, query, ranked, output_path, offline=offline)
    return PipelineResult(
        question=question,
        output_dir=output_path,
        ranked_candidates=tuple(ranked),
        artifact_paths=tuple(artifacts),
    )


def _collect_candidates(query, offline: bool, limit: int) -> list[DatasetCandidate]:
    if offline:
        return StaticCatalogConnector().search(query, limit=limit)

    candidates: list[DatasetCandidate] = []
    try:
        candidates.extend(DandiConnector().search(query, limit=limit))
    except Exception:
        # Network/API failure must not make local artifact generation unusable.
        # The provenance/report will still mark fallback candidates as offline seed metadata.
        candidates = []
    if len(candidates) < limit:
        existing = {candidate.identifier for candidate in candidates}
        for fallback in StaticCatalogConnector().search(query, limit=limit):
            if fallback.identifier not in existing:
                candidates.append(fallback)
            if len(candidates) >= limit:
                break
    return candidates
