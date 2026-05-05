from __future__ import annotations

import re

from neurocartographer.models import QuerySpec

_SPECIES_TERMS = {
    "mouse": ("mouse", "mice", "murine"),
    "rat": ("rat", "rats"),
    "human": ("human", "humans", "participant", "participants", "subject", "subjects"),
    "macaque": ("macaque", "monkey", "nonhuman primate", "non-human primate"),
}

_REGION_TERMS = {
    "visual cortex": ("visual cortex", "v1", "visual"),
    "hippocampus": ("hippocampus", "hippocampal", "ca1", "ca3", "dentate"),
    "motor cortex": ("motor cortex", "m1", "motor"),
    "prefrontal cortex": ("prefrontal", "pfc", "frontal cortex"),
    "auditory cortex": ("auditory cortex", "auditory"),
}

_MODALITY_TERMS = {
    "calcium imaging": ("calcium imaging", "two-photon", "2-photon", "ophys", "gcamp"),
    "extracellular electrophysiology": ("extracellular", "neuropixels", "spikes", "spike", "ephys"),
    "intracellular electrophysiology": ("intracellular", "patch clamp", "patch-clamp"),
    "fMRI": ("fmri", "bold"),
    "EEG": ("eeg",),
    "MEG": ("meg",),
    "behavior": ("behavior", "behaviour", "locomotion", "navigation", "task"),
}

_KEYWORD_PHRASES = (
    "sharp wave ripple",
    "replay",
    "navigation",
    "decision making",
    "locomotion",
    "naturalistic",
    "stimulus",
    "behavior",
)


def parse_question(question: str) -> QuerySpec:
    """Parse a plain-language neuroscience question into transparent search constraints."""
    normalized = _normalize(question)
    species = _matches(normalized, _SPECIES_TERMS)
    brain_regions = _matches(normalized, _REGION_TERMS)
    modalities = _matches(normalized, _MODALITY_TERMS)
    keywords = _extract_keywords(normalized, modalities)
    search_terms = _build_search_terms(species, brain_regions, modalities, keywords, normalized)
    return QuerySpec(
        original_question=question.strip(),
        species=tuple(species),
        brain_regions=tuple(brain_regions),
        modalities=tuple(modalities),
        keywords=tuple(keywords),
        search_terms=tuple(search_terms),
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _matches(text: str, dictionary: dict[str, tuple[str, ...]]) -> list[str]:
    found: list[str] = []
    for canonical, aliases in dictionary.items():
        if any(_contains_phrase(text, alias) for alias in aliases):
            found.append(canonical)
    return found


def _extract_keywords(text: str, modalities: list[str]) -> list[str]:
    keywords: list[str] = []
    for phrase in _KEYWORD_PHRASES:
        if _contains_phrase(text, phrase):
            keywords.append(phrase)
    for modality in modalities:
        if modality == "behavior" and "behavior" not in keywords:
            keywords.append("behavior")
    return _unique(keywords)


def _build_search_terms(
    species: list[str],
    regions: list[str],
    modalities: list[str],
    keywords: list[str],
    normalized_question: str,
) -> list[str]:
    preferred_terms = [*species, *regions, *modalities, *keywords]
    preferred_terms = [term for term in preferred_terms if term != "behavior"] + [
        term for term in preferred_terms if term == "behavior"
    ]
    compact = " ".join(_unique(preferred_terms))
    if compact:
        return [compact]
    return [normalized_question]


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase.lower())
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
