import json
from pathlib import Path

from neurocartographer.pipeline import run_pipeline


def test_pipeline_writes_reproducibility_artifacts(tmp_path: Path):
    result = run_pipeline(
        question="Find mouse visual cortex calcium imaging datasets with behavior",
        output_dir=tmp_path,
        offline=True,
        limit=3,
    )

    expected = {
        "dataset_cards.md",
        "qc_report.md",
        "starter_analysis.ipynb",
        "provenance.json",
        "run_manifest.json",
    }
    assert expected <= {path.name for path in result.artifact_paths}

    manifest = json.loads((tmp_path / "run_manifest.json").read_text())
    assert manifest["question"] == "Find mouse visual cortex calcium imaging datasets with behavior"
    assert manifest["offline"] is True
    assert manifest["top_dataset"]["identifier"] == "DANDI:000728"

    notebook = json.loads((tmp_path / "starter_analysis.ipynb").read_text())
    assert notebook["nbformat"] == 4
    assert any("Trust contract" in cell.get("source", "") for cell in notebook["cells"])

    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["claim_policy"] == "no_scientific_claims_without_executed_evidence"
    assert provenance["ranked_candidates"][0]["identifier"] == "DANDI:000728"
