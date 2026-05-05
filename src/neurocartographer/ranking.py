from __future__ import annotations

from neurocartographer.models import DatasetCandidate, QuerySpec, RankedCandidate


def rank_candidates(query: QuerySpec, candidates: list[DatasetCandidate]) -> list[RankedCandidate]:
    ranked = [_score_candidate(query, candidate) for candidate in candidates]
    return sorted(ranked, key=lambda item: (-item.score, item.candidate.identifier))


def _score_candidate(query: QuerySpec, candidate: DatasetCandidate) -> RankedCandidate:
    score = 0.0
    reasons: list[str] = []
    score += _score_matches("species", query.species, candidate.species, reasons, weight=3.0)
    score += _score_matches("brain region", query.brain_regions, candidate.brain_regions, reasons, weight=3.0)
    score += _score_matches("modality", query.modalities, candidate.modalities, reasons, weight=2.5)
    score += _score_matches("keyword", query.keywords, candidate.keywords, reasons, weight=1.0)
    if candidate.metadata.get("standard") in {"NWB", "BIDS"}:
        score += 1.0
        reasons.append(f"standard: {candidate.metadata['standard']}")
    if candidate.metadata.get("access") == "open":
        score += 1.0
        reasons.append("access: open")
    if not reasons:
        reasons.append("weak text/catalog match only")
    return RankedCandidate(candidate=candidate, score=round(score, 3), reasons=tuple(reasons))


def _score_matches(
    label: str,
    requested: tuple[str, ...],
    available: tuple[str, ...],
    reasons: list[str],
    weight: float,
) -> float:
    if not requested:
        return 0.0
    available_set = {item.lower() for item in available}
    total = 0.0
    for item in requested:
        if item.lower() in available_set:
            total += weight
            reasons.append(f"{label}: {item}")
    return total
