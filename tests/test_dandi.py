from neurocartographer.connectors.dandi import _candidate_from_dandi


def test_dandi_candidate_parser_reads_current_nested_version_payload():
    item = {
        "identifier": "000036",
        "draft_version": {
            "name": "Allen Institute Openscope - Mouse Visual Cortex Calcium Imaging Behavior",
            "description": "Two-photon calcium imaging from mouse visual cortex with behavior.",
            "asset_count": 12,
        },
        "most_recent_published_version": {
            "name": "Older published title",
            "description": "Older description",
        },
    }

    candidate = _candidate_from_dandi(item)

    assert candidate.identifier == "DANDI:000036"
    assert candidate.title == "Allen Institute Openscope - Mouse Visual Cortex Calcium Imaging Behavior"
    assert "mouse" in candidate.species
    assert "visual cortex" in candidate.brain_regions
    assert "calcium imaging" in candidate.modalities
    assert "behavior" in candidate.modalities
    assert candidate.metadata["asset_count"] == 12


def test_dandi_candidate_parser_falls_back_to_published_version():
    item = {
        "identifier": "000037",
        "most_recent_published_version": {
            "name": "Human EEG resting-state BIDS dataset",
            "description": "Open EEG recordings from human subjects.",
        },
    }

    candidate = _candidate_from_dandi(item)

    assert candidate.title == "Human EEG resting-state BIDS dataset"
    assert "human" in candidate.species
    assert "EEG" in candidate.modalities
