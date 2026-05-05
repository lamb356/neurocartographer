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
class AssetInfo:
    path: str
    size_bytes: int | None = None
    url: str | None = None
    standard: str = "unknown"
    modality_hint: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


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
class DatasetInspection:
    candidate_identifier: str
    asset_count: int
    nwb_asset_count: int
    bids_file_count: int
    total_size_bytes: int | None
    standard_summary: str
    inferred_modalities: tuple[str, ...]
    representative_assets: tuple[AssetInfo, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class NotebookExecutionReport:
    status: str
    backend: str
    executed_cell_count: int
    stdout: str = ""
    stderr: str = ""
    reason: str = ""
    elapsed_seconds: float = 0.0


@dataclass(frozen=True)
class ArtifactBundle:
    output_dir: str
    artifact_paths: tuple[str, ...]
