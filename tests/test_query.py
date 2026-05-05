from neurocartographer.query import parse_question


def test_parse_question_extracts_neuroscience_constraints():
    spec = parse_question("Find mouse visual cortex calcium imaging datasets with behavior")

    assert spec.original_question == "Find mouse visual cortex calcium imaging datasets with behavior"
    assert "mouse" in spec.species
    assert "visual cortex" in spec.brain_regions
    assert "calcium imaging" in spec.modalities
    assert "behavior" in spec.keywords
    assert spec.search_terms[0] == "mouse visual cortex calcium imaging behavior"


def test_parse_question_keeps_unknown_terms_as_keywords():
    spec = parse_question("hippocampal replay navigation sharp wave ripple")

    assert "hippocampus" in spec.brain_regions
    assert "navigation" in spec.keywords
    assert "sharp wave ripple" in spec.keywords
