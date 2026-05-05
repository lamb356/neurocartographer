from __future__ import annotations

import re

_OPHYS_TOKEN_RE = re.compile(r"(^|[^a-z])ophys([^a-z]|$)")


def has_ophys_token(text: str) -> bool:
    """Return true for ophys as a token/path component, not inside neurophysiology."""

    return _OPHYS_TOKEN_RE.search(text.lower()) is not None


def has_calcium_imaging_signal(text: str) -> bool:
    lower = text.lower()
    return has_ophys_token(lower) or any(token in lower for token in ("calcium", "two-photon", "2-photon"))


def modality_hint_from_path(path: str) -> str | None:
    lower = path.lower()
    if "eeg" in lower:
        return "EEG"
    if "meg" in lower:
        return "MEG"
    if "bold" in lower or "fmri" in lower:
        return "fMRI"
    if has_calcium_imaging_signal(lower):
        return "calcium imaging"
    if "behavior" in lower or "behaviour" in lower:
        return "behavior"
    if "ecephys" in lower or "neuropixels" in lower or "_ephys" in lower or "/ephys" in lower or "ephys_" in lower:
        return "extracellular electrophysiology"
    return None
