from __future__ import annotations

from neurocartographer.models import AssetInfo, DatasetCandidate, DatasetInspection
from neurocartographer.modalities import has_calcium_imaging_signal


def summarize_assets(candidate: DatasetCandidate, assets: tuple[AssetInfo, ...]) -> DatasetInspection:
    total_size = _sum_known_sizes(assets)
    nwb_assets = tuple(asset for asset in assets if asset.standard == "NWB" or asset.path.lower().endswith(".nwb"))
    bids_files = tuple(asset for asset in assets if asset not in nwb_assets and _looks_like_bids_path(asset.path))
    modalities = _infer_modalities(candidate, assets)
    standards = []
    if nwb_assets:
        standards.append("NWB")
    if bids_files or candidate.metadata.get("standard") == "BIDS":
        standards.append("BIDS")
    standard_summary = ", ".join(dict.fromkeys(standards)) if standards else str(candidate.metadata.get("standard") or "unknown")
    warnings: list[str] = []
    if not assets:
        warnings.append("No asset inventory was available for this candidate.")
    if candidate.source == "DANDI" and not nwb_assets:
        warnings.append("No NWB assets were detected in the inspected DANDI asset preview.")
    if any(asset.metadata.get("source") == "default_bids_pattern" for asset in assets):
        warnings.append("OpenNeuro file tree was not fetched; assets shown are default inferred BIDS patterns.")
    return DatasetInspection(
        candidate_identifier=candidate.identifier,
        asset_count=len(assets),
        nwb_asset_count=len(nwb_assets),
        bids_file_count=len(bids_files),
        total_size_bytes=total_size,
        standard_summary=standard_summary,
        inferred_modalities=tuple(modalities),
        representative_assets=tuple(assets[:10]),
        warnings=tuple(warnings),
    )


def _sum_known_sizes(assets: tuple[AssetInfo, ...]) -> int | None:
    sizes = [asset.size_bytes for asset in assets if asset.size_bytes is not None]
    return sum(sizes) if sizes else None


def _looks_like_bids_path(path: str) -> bool:
    lower = path.lower().rstrip("/")
    return (
        lower == "dataset_description.json"
        or lower == "participants.tsv"
        or lower.startswith("sub-")
        or "/sub-" in lower
        or "_bold." in lower
        or "_eeg." in lower
        or "_meg." in lower
        or "_ieeg." in lower
    )


def _infer_modalities(candidate: DatasetCandidate, assets: tuple[AssetInfo, ...]) -> list[str]:
    joined = " ".join([candidate.description, candidate.title, *candidate.modalities, *(asset.path for asset in assets)]).lower()
    modalities: list[str] = []
    if has_calcium_imaging_signal(joined):
        modalities.append("calcium imaging")
    if any(token in joined for token in ("behavior", "behaviour", "locomotion", "running")):
        modalities.append("behavior")
    if any(token in joined for token in ("ecephys", "neuropixels", "electrophysiology", "spike")):
        modalities.append("extracellular electrophysiology")
    if "eeg" in joined:
        modalities.append("EEG")
    if "meg" in joined:
        modalities.append("MEG")
    if any(token in joined for token in ("fmri", "bold", "mri")):
        modalities.append("fMRI")
    return list(dict.fromkeys(modalities))
