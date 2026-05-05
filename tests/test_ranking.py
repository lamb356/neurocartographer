from neurocartographer.connectors.static_catalog import StaticCatalogConnector
from neurocartographer.query import parse_question
from neurocartographer.ranking import rank_candidates


def test_rank_candidates_prefers_dataset_matching_modalities_species_and_region():
    spec = parse_question("Find mouse visual cortex calcium imaging datasets with behavior")
    candidates = StaticCatalogConnector().search(spec, limit=10)

    ranked = rank_candidates(spec, candidates)

    assert ranked[0].candidate.identifier == "DANDI:000728"
    assert ranked[0].score > ranked[-1].score
    joined_reasons = " ".join(ranked[0].reasons)
    assert "species: mouse" in joined_reasons
    assert "modality: calcium imaging" in joined_reasons
    assert "brain region: visual cortex" in joined_reasons


def test_rank_candidates_is_stable_for_empty_candidate_list():
    spec = parse_question("unknown task")
    assert rank_candidates(spec, []) == []
