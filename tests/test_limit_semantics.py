from pathlib import Path

from neurocartographer.pipeline import run_pipeline


def test_limit_is_applied_after_ranking_for_human_eeg_query(tmp_path: Path):
    result = run_pipeline("human EEG dataset", tmp_path, offline=True, limit=1)

    assert len(result.ranked_candidates) == 1
    assert result.ranked_candidates[0].candidate.identifier == "OpenNeuro:ds004504"


def test_limit_is_applied_after_ranking_for_hippocampal_query(tmp_path: Path):
    result = run_pipeline("hippocampal replay navigation sharp wave ripple", tmp_path, offline=True, limit=1)

    assert len(result.ranked_candidates) == 1
    assert result.ranked_candidates[0].candidate.identifier == "SEED:hippocampal-replay-navigation"
