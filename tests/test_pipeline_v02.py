import json
from pathlib import Path

from neurocartographer.pipeline import run_pipeline


def test_pipeline_generates_asset_nwb_and_execution_artifacts(tmp_path: Path):
    result = run_pipeline(
        "Find mouse visual cortex calcium imaging datasets with behavior",
        tmp_path,
        offline=True,
        limit=2,
        execute_notebook=True,
    )

    names = {path.name for path in result.artifact_paths}
    assert "asset_inventory.md" in names
    assert "nwb_summary.md" in names
    assert "execution_report.json" in names

    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution"]["status"] == "passed"
    assert manifest["inspection"]["inspected_dataset_count"] >= 1

    nwb_summary = (tmp_path / "nwb_summary.md").read_text(encoding="utf-8")
    assert "NWB assets" in nwb_summary
    assert "calcium imaging" in nwb_summary
