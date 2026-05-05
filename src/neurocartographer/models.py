from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QuerySpec:
    original_question: str
    species: tuple[str, ...] = ()
    brain_regions: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    search_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatasetCandidate:
    identifier: str
    title: str
    source: str
    url: str
    description: str
    species: tuple[str, ...] = ()
    brain_regions: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    assets: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RankedCandidate:
    candidate: DatasetCandidate
    score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ArtifactBundle:
    output_dir: str
    artifact_paths: tuple[str, ...]
