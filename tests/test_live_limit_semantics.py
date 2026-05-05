import json
from pathlib import Path

from neurocartographer.pipeline import run_pipeline


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_live_connector_collects_candidate_pool_before_pipeline_limit(monkeypatch, tmp_path: Path):
    payload = {
        "results": [
            {
                "identifier": "999999",
                "draft_version": {
                    "name": "Generic unrelated NWB archive",
                    "description": "Open metadata with no query-relevant terms.",
                },
            },
            {
                "identifier": "000036",
                "draft_version": {
                    "name": "Mouse visual cortex calcium imaging behavior",
                    "description": "Two-photon calcium imaging from mouse visual cortex with behavior.",
                },
            },
        ]
    }

    def fake_urlopen(request, timeout):
        return _FakeResponse(payload)

    monkeypatch.setattr("neurocartographer.connectors.dandi.urllib.request.urlopen", fake_urlopen)

    result = run_pipeline(
        "mouse visual cortex calcium imaging behavior",
        tmp_path,
        offline=False,
        limit=1,
    )

    assert result.ranked_candidates[0].candidate.identifier == "DANDI:000036"
