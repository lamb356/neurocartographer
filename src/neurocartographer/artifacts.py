from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from neurocartographer.models import QuerySpec, RankedCandidate

CLAIM_POLICY = "no_scientific_claims_without_executed_evidence"


def write_artifacts(question: str, query: QuerySpec, ranked: list[RankedCandidate], output_dir: Path, offline: bool) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = [
        output_dir / "dataset_cards.md",
        output_dir / "qc_report.md",
        output_dir / "starter_analysis.ipynb",
        output_dir / "provenance.json",
        output_dir / "run_manifest.json",
    ]
    _write_dataset_cards(artifact_paths[0], question, ranked)
    _write_qc_report(artifact_paths[1], query, ranked, offline)
    _write_notebook(artifact_paths[2], question, ranked)
    _write_provenance(artifact_paths[3], question, query, ranked, offline)
    _write_manifest(artifact_paths[4], question, ranked, artifact_paths, offline)
    return artifact_paths


def _write_dataset_cards(path: Path, question: str, ranked: list[RankedCandidate]) -> None:
    lines = [f"# Dataset cards for: {question}", "", "## Ranking summary", ""]
    for index, item in enumerate(ranked, start=1):
        c = item.candidate
        lines.extend(
            [
                f"### {index}. {c.identifier} — {c.title}",
                "",
                f"- Source: {c.source}",
                f"- URL: {c.url}",
                f"- Score: {item.score}",
                f"- Species: {_format_tuple(c.species)}",
                f"- Brain regions: {_format_tuple(c.brain_regions)}",
                f"- Modalities: {_format_tuple(c.modalities)}",
                f"- Assets: {_format_tuple(c.assets)}",
                f"- Fit reasons: {_format_tuple(item.reasons)}",
                f"- Description: {c.description}",
                "",
            ]
        )
    if not ranked:
        lines.append("No candidates were found.")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_qc_report(path: Path, query: QuerySpec, ranked: list[RankedCandidate], offline: bool) -> None:
    top = ranked[0].candidate if ranked else None
    lines = [
        "# QC and trust report",
        "",
        f"- Claim policy: `{CLAIM_POLICY}`",
        f"- Offline mode: `{offline}`",
        f"- Parsed species: {_format_tuple(query.species)}",
        f"- Parsed brain regions: {_format_tuple(query.brain_regions)}",
        f"- Parsed modalities: {_format_tuple(query.modalities)}",
        f"- Parsed keywords: {_format_tuple(query.keywords)}",
        "",
        "## Verified",
        "",
        "- Artifact files were generated locally.",
        "- Notebook JSON structure was generated deterministically.",
    ]
    if top:
        lines.append(f"- Top candidate metadata source: `{top.metadata.get('verification', 'unknown')}`.")
    lines.extend(
        [
            "",
            "## Inferred",
            "",
            "- Dataset fit is based on transparent metadata/text matching, not scientific result computation.",
            "",
            "## Unknown / not yet verified",
            "",
            "- Whether the top dataset truly answers the scientific question requires executing dataset-specific analysis.",
            "- Remote asset availability is not checked in offline mode.",
            "- No scientific finding is claimed by this starter package.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_notebook(path: Path, question: str, ranked: list[RankedCandidate]) -> None:
    top = ranked[0].candidate if ranked else None
    cells = [
        _markdown_cell(
            "# NeuroCartographer starter analysis\n\n"
            f"Question: {question}\n\n"
            "## Trust contract\n\n"
            "This notebook is a starter scaffold. It must not be used to claim a scientific result until the data-loading and analysis cells run successfully and the outputs are captured."
        ),
        _markdown_cell("## Selected dataset\n\n" + (_dataset_markdown(top) if top else "No dataset candidate selected.")),
        _code_cell(
            "from pathlib import Path\n"
            "import json\n\n"
            "print('NeuroCartographer starter notebook loaded')\n"
        ),
        _code_cell(
            "# Next step: install domain packages as needed, for example:\n"
            "#   pip install dandi pynwb remfile matplotlib\n"
            "# Then use the selected dataset URL/identifier above to stream or download NWB assets.\n"
            "selected_dataset = " + json.dumps(top.identifier if top else None) + "\n"
            "selected_url = " + json.dumps(top.url if top else None) + "\n"
            "print({'selected_dataset': selected_dataset, 'selected_url': selected_url})\n"
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {"language_info": {"name": "python", "pygments_lexer": "ipython3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")


def _write_provenance(path: Path, question: str, query: QuerySpec, ranked: list[RankedCandidate], offline: bool) -> None:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "offline": offline,
        "claim_policy": CLAIM_POLICY,
        "query_spec": {
            "species": list(query.species),
            "brain_regions": list(query.brain_regions),
            "modalities": list(query.modalities),
            "keywords": list(query.keywords),
            "search_terms": list(query.search_terms),
        },
        "ranked_candidates": [_ranked_to_dict(item) for item in ranked],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_manifest(path: Path, question: str, ranked: list[RankedCandidate], artifact_paths: list[Path], offline: bool) -> None:
    payload = {
        "question": question,
        "offline": offline,
        "artifact_count": len(artifact_paths),
        "artifacts": [artifact.name for artifact in artifact_paths],
        "top_dataset": _candidate_summary(ranked[0]) if ranked else None,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _ranked_to_dict(item: RankedCandidate) -> dict[str, object]:
    c = item.candidate
    return {
        "identifier": c.identifier,
        "title": c.title,
        "source": c.source,
        "url": c.url,
        "score": item.score,
        "reasons": list(item.reasons),
        "metadata": c.metadata,
    }


def _candidate_summary(item: RankedCandidate) -> dict[str, object]:
    return {"identifier": item.candidate.identifier, "title": item.candidate.title, "score": item.score}


def _dataset_markdown(candidate) -> str:
    return (
        f"- Identifier: `{candidate.identifier}`\n"
        f"- Title: {candidate.title}\n"
        f"- Source: {candidate.source}\n"
        f"- URL: {candidate.url}\n"
        f"- Modalities: {_format_tuple(candidate.modalities)}\n"
    )


def _markdown_cell(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def _code_cell(source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source}


def _format_tuple(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "unknown"
