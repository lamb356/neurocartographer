from neurocartographer.inspection import summarize_assets
from neurocartographer.models import AssetInfo, DatasetCandidate


def test_summarize_assets_reports_nwb_counts_modalities_and_size():
    candidate = DatasetCandidate(
        identifier="DANDI:000728",
        title="Mouse visual cortex ophys",
        source="DANDI",
        url="https://dandiarchive.org/dandiset/000728",
        description="mouse visual cortex two-photon calcium imaging behavior",
    )
    assets = (
        AssetInfo(path="sub-01/sub-01_ophys.nwb", size_bytes=100, standard="NWB"),
        AssetInfo(path="sub-01/sub-01_behavior.nwb", size_bytes=50, standard="NWB"),
    )

    summary = summarize_assets(candidate, assets)

    assert summary.asset_count == 2
    assert summary.nwb_asset_count == 2
    assert summary.total_size_bytes == 150
    assert "calcium imaging" in summary.inferred_modalities
    assert "behavior" in summary.inferred_modalities
    assert summary.standard_summary == "NWB"
