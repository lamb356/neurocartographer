import json

from neurocartographer.connectors.openneuro import OpenNeuroConnector, parse_openneuro_payload
from neurocartographer.query import parse_question
from neurocartographer.ranking import rank_candidates


class _FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _payload():
    return {
        "data": {
            "datasets": {
                "edges": [
                    {
                        "node": {
                            "id": "ds004504",
                            "name": "Human EEG resting-state example",
                            "public": True,
                            "metadata": {
                                "datasetName": "Human EEG resting-state example",
                                "species": "human",
                                "modalities": ["eeg"],
                                "studyDomain": "resting state",
                                "trialCount": 12,
                            },
                            "latestSnapshot": {
                                "tag": "1.0.0",
                                "description": {"Name": "Human EEG resting-state example", "DatasetType": "raw"},
                                "files": [
                                    {"filename": "dataset_description.json", "size": 500, "directory": False, "annexed": False},
                                    {"filename": "sub-01", "size": 0, "directory": True, "annexed": False},
                                ],
                            },
                        }
                    }
                ]
            }
        }
    }


def test_parse_openneuro_payload_returns_bids_candidate_with_assets():
    candidates = parse_openneuro_payload(_payload())

    assert candidates[0].identifier == "OpenNeuro:ds004504"
    assert candidates[0].metadata["standard"] == "BIDS"
    assert candidates[0].metadata["snapshot_tag"] == "1.0.0"
    assert candidates[0].assets == ("dataset_description.json", "sub-01/")
    assert "EEG" in candidates[0].modalities


def test_openneuro_connector_fetches_and_ranks_human_eeg(monkeypatch):
    def fake_urlopen(request, timeout):
        return _FakeResponse(_payload())

    monkeypatch.setattr("neurocartographer.connectors.openneuro.urllib.request.urlopen", fake_urlopen)
    query = parse_question("human EEG resting-state dataset")
    candidates = OpenNeuroConnector().search(query, limit=1)
    ranked = rank_candidates(query, candidates)

    assert ranked[0].candidate.identifier == "OpenNeuro:ds004504"
    assert ranked[0].score > 0
