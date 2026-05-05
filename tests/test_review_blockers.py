from pathlib import Path

from neurocartographer.connectors.dandi import _asset_modality_hint, _candidate_from_dandi, _detect_modalities
from neurocartographer.execution import execute_notebook
from neurocartographer.inspection import summarize_assets
from neurocartographer.models import AssetInfo, DatasetCandidate
from neurocartographer.pipeline import _asset_from_path, _candidate_assets


def test_electrophysiology_does_not_imply_calcium_imaging():
    candidate = DatasetCandidate(
        identifier="SEED:ephys",
        title="Hippocampal electrophysiology and behavior",
        source="OfflineSeed",
        url="https://example.test",
        description="mouse neurophysiology electrophysiology behavior dataset",
        modalities=("extracellular electrophysiology", "behavior"),
    )
    assets = (AssetInfo(path="sub-01/sub-01_ecephys.nwb", standard="NWB"),)

    summary = summarize_assets(candidate, assets)

    assert "extracellular electrophysiology" in summary.inferred_modalities
    assert "calcium imaging" not in summary.inferred_modalities


def test_eeg_neurophysiology_does_not_imply_calcium_imaging():
    candidate = DatasetCandidate(
        identifier="OpenNeuro:ds004504",
        title="Human EEG neurophysiology",
        source="OpenNeuro",
        url="https://openneuro.org/datasets/ds004504",
        description="human clinical neurophysiology EEG resting state dataset",
        modalities=("EEG",),
    )
    assets = (AssetInfo(path="sub-01/eeg/sub-01_task-rest_eeg.set", standard="BIDS"),)

    summary = summarize_assets(candidate, assets)

    assert "EEG" in summary.inferred_modalities
    assert "calcium imaging" not in summary.inferred_modalities


def test_dandi_modality_detectors_do_not_treat_neurophysiology_as_ophys():
    candidate = _candidate_from_dandi(
        {
            "identifier": "TEST",
            "draft_version": {
                "name": "Human neurophysiology EEG dataset",
                "description": "human EEG electrophysiology recordings",
            },
        }
    )

    assert "EEG" in candidate.modalities
    assert "extracellular electrophysiology" in candidate.modalities
    assert "calcium imaging" not in candidate.modalities
    assert "calcium imaging" not in _detect_modalities("human clinical neurophysiology eeg electrophysiology dataset")
    assert _asset_modality_hint("sub-01/sub-01_neurophysiology.nwb") is None


def test_pipeline_asset_hint_does_not_treat_neurophysiology_as_ophys():
    asset = _asset_from_path("sub-01/eeg/sub-01_task-neurophysiology_eeg.set")

    assert asset.modality_hint == "EEG"


def test_openneuro_default_bids_patterns_are_marked_as_inferred():
    candidate = DatasetCandidate(
        identifier="OpenNeuro:synthetic",
        title="Human EEG dataset",
        source="OpenNeuro",
        url="https://openneuro.org/datasets/synthetic",
        description="human EEG dataset",
        modalities=("EEG",),
        assets=("dataset_description.json", "participants.tsv", "sub-*/eeg/*_eeg.*"),
        metadata={"standard": "BIDS", "asset_preview_source": "default_bids_patterns"},
    )

    assets = _candidate_assets(candidate)
    summary = summarize_assets(candidate, assets)

    assert all(asset.metadata.get("source") == "default_bids_pattern" for asset in assets)
    assert any("default inferred BIDS patterns" in warning for warning in summary.warnings)


def test_execute_notebook_timeout_writes_timed_out_report(tmp_path: Path):
    notebook = tmp_path / "hang.ipynb"
    report_path = tmp_path / "execution_report.json"
    notebook.write_text(
        '{"cells":[{"cell_type":"code","source":"while True:\\n    pass"}],"metadata":{},"nbformat":4,"nbformat_minor":5}',
        encoding="utf-8",
    )

    report = execute_notebook(notebook, report_path, timeout_seconds=1)

    assert report.status == "timed_out"
    assert report_path.exists()
