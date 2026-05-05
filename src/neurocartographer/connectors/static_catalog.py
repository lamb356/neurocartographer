from __future__ import annotations

from neurocartographer.models import DatasetCandidate, QuerySpec


class StaticCatalogConnector:
    """Small built-in catalog that keeps demos/tests useful without network access."""

    name = "static-catalog"

    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]:
        if limit <= 0:
            return []
        # Return the whole deterministic seed catalog so the pipeline can rank
        # before slicing to the requested top-N. Truncating before ranking makes
        # --limit 1 return the first catalog row rather than the best fit.
        return list(_CATALOG)


_CATALOG = (
    DatasetCandidate(
        identifier="DANDI:000728",
        title="Allen Institute Openscope-style mouse visual cortex ophys with behavior",
        source="DANDI",
        url="https://dandiarchive.org/dandiset/000728",
        description=(
            "Representative NWB/DANDI-style candidate for mouse visual cortex calcium imaging "
            "with behavioral covariates and visual stimulus responses."
        ),
        species=("mouse",),
        brain_regions=("visual cortex",),
        modalities=("calcium imaging", "behavior"),
        keywords=("visual stimulus", "locomotion", "behavior"),
        assets=("sub-*/sub-*_ophys.nwb",),
        metadata={"standard": "NWB", "access": "open", "verification": "offline_seed_catalog"},
    ),
    DatasetCandidate(
        identifier="SEED:hippocampal-replay-navigation",
        title="Illustrative hippocampal replay/navigation NWB seed dataset",
        source="OfflineSeed",
        url="https://dandiarchive.org/",
        description=(
            "Illustrative offline seed candidate for hippocampal replay, sharp-wave ripple, "
            "navigation, and behavior workflows. It is intentionally not presented as a "
            "verified DANDI dandiset."
        ),
        species=("mouse",),
        brain_regions=("hippocampus",),
        modalities=("extracellular electrophysiology", "behavior"),
        keywords=("navigation", "replay", "sharp wave ripple"),
        assets=("sub-*/sub-*_ecephys.nwb",),
        metadata={"standard": "NWB", "access": "open", "verification": "illustrative_offline_seed_not_live_verified"},
    ),
    DatasetCandidate(
        identifier="OpenNeuro:ds004504",
        title="EEG recordings from Alzheimer's disease, frontotemporal dementia, and healthy subjects",
        source="OpenNeuro",
        url="https://openneuro.org/datasets/ds004504",
        description="Representative BIDS EEG candidate useful for human clinical/neurophysiology pipeline demos.",
        species=("human",),
        brain_regions=(),
        modalities=("EEG",),
        keywords=("clinical", "resting state"),
        assets=("sub-*/eeg/*.set",),
        metadata={"standard": "BIDS", "access": "open", "verification": "offline_seed_catalog"},
    ),
)
