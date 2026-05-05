from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from neurocartographer.execution import execute_notebook
from neurocartographer.models import DatasetInspection, NotebookExecutionReport, QuerySpec, RankedCandidate

CLAIM_POLICY = "no_scientific_claims_without_executed_evidence"


def write_artifacts(
    question: str,
    query: QuerySpec,
    ranked: list[RankedCandidate],
    inspections: tuple[DatasetInspection, ...],
    output_dir: Path,
    offline: bool,
    execute_notebook: bool = False,
) -> tuple[list[Path], NotebookExecutionReport | None]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_cards = output_dir / "dataset_cards.md"
    qc_report = output_dir / "qc_report.md"
    notebook = output_dir / "starter_analysis.ipynb"
    asset_inventory = output_dir / "asset_inventory.md"
    nwb_summary = output_dir / "nwb_summary.md"
    provenance = output_dir / "provenance.json"
    manifest = output_dir / "run_manifest.json"

    _write_dataset_cards(dataset_cards, question, ranked)
    _write_asset_inventory(asset_inventory, inspections)
    _write_nwb_summary(nwb_summary, inspections)
    _write_notebook(notebook, question, ranked, inspections)

    execution_report = None
    artifact_paths = [dataset_cards, qc_report, notebook, asset_inventory, nwb_summary, provenance, manifest]
    execution_report_path = output_dir / "execution_report.json"
    if execute_notebook:
        execution_report = execute_notebook_fn(notebook, execution_report_path)
        artifact_paths.insert(5, execution_report_path)

    _write_qc_report(qc_report, query, ranked, inspections, offline, execution_report)
    _write_provenance(provenance, question, query, ranked, inspections, offline, execution_report)
    _write_manifest(manifest, question, ranked, inspections, artifact_paths, offline, execution_report)
    return artifact_paths, execution_report


def execute_notebook_fn(notebook: Path, report_path: Path) -> NotebookExecutionReport:
    return execute_notebook(notebook, report_path)


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


def _write_asset_inventory(path: Path, inspections: tuple[DatasetInspection, ...]) -> None:
    lines = ["# Asset inventory", ""]
    for inspection in inspections:
        lines.extend(
            [
                f"## {inspection.candidate_identifier}",
                "",
                f"- Asset preview count: {inspection.asset_count}",
                f"- Total known size: {_format_size(inspection.total_size_bytes)}",
                f"- Standards detected: {inspection.standard_summary}",
                "",
                "| Path | Size | Standard | Modality hint |",
                "| --- | ---: | --- | --- |",
            ]
        )
        for asset in inspection.representative_assets:
            lines.append(
                f"| `{asset.path}` | {_format_size(asset.size_bytes)} | {asset.standard} | {asset.modality_hint or 'unknown'} |"
            )
        if not inspection.representative_assets:
            lines.append("| _none_ | unknown | unknown | unknown |")
        if inspection.warnings:
            lines.extend(["", "Warnings:"] + [f"- {warning}" for warning in inspection.warnings])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_nwb_summary(path: Path, inspections: tuple[DatasetInspection, ...]) -> None:
    lines = ["# NWB/BIDS metadata summary", ""]
    for inspection in inspections:
        lines.extend(
            [
                f"## {inspection.candidate_identifier}",
                "",
                f"- Standards: {inspection.standard_summary}",
                f"- NWB assets: {inspection.nwb_asset_count}",
                f"- BIDS-like files/directories: {inspection.bids_file_count}",
                f"- Inferred modalities: {_format_tuple(inspection.inferred_modalities)}",
                f"- Total known size: {_format_size(inspection.total_size_bytes)}",
                "",
            ]
        )
    if not inspections:
        lines.append("No candidates were inspected.")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_qc_report(
    path: Path,
    query: QuerySpec,
    ranked: list[RankedCandidate],
    inspections: tuple[DatasetInspection, ...],
    offline: bool,
    execution_report: NotebookExecutionReport | None,
) -> None:
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
        f"- Dataset asset previews inspected: `{len(inspections)}`.",
    ]
    if top:
        lines.append(f"- Top candidate metadata source: `{top.metadata.get('verification', 'unknown')}`.")
    if execution_report:
        lines.append(f"- Generated notebook execution status: `{execution_report.status}` via `{execution_report.backend}`.")
    lines.extend(
        [
            "",
            "## Inferred",
            "",
            "- Dataset fit is based on transparent metadata/text matching, not scientific result computation.",
            "- NWB/BIDS modality summaries are inferred from metadata and asset paths unless a future optional reader verifies file internals.",
            "",
            "## Unknown / not yet verified",
            "",
            "- Whether the top dataset truly answers the scientific question requires executing dataset-specific analysis on real data arrays.",
            "- Remote asset availability is not checked in offline mode.",
            "- No scientific finding is claimed by this starter package.",
        ]
    )
    if execution_report and "not a hardened" in _execution_security_note():
        lines.extend(["", "## Execution safety note", "", f"- {_execution_security_note()}"])
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_notebook(
    path: Path,
    question: str,
    ranked: list[RankedCandidate],
    inspections: tuple[DatasetInspection, ...],
) -> None:
    top = ranked[0].candidate if ranked else None
    top_inspection = inspections[0] if inspections else None
    asset_paths = [asset.path for asset in top_inspection.representative_assets] if top_inspection else []
    cells = [
        _markdown_cell(
            "# NeuroCartographer starter analysis\n\n"
            f"Question: {question}\n\n"
            "## Trust contract\n\n"
            "This notebook is a starter scaffold. It must not be used to claim a scientific result until data-loading and analysis cells run successfully against real data arrays and outputs are captured."
        ),
        _markdown_cell("## Selected dataset\n\n" + (_dataset_markdown(top) if top else "No dataset candidate selected.")),
        _markdown_cell("## Inspected asset summary\n\n" + (_inspection_markdown(top_inspection) if top_inspection else "No asset inspection available.")),
        _code_cell(
            "import json\n\n"
            "selected_dataset = " + json.dumps(top.identifier if top else None) + "\n"
            "selected_url = " + json.dumps(top.url if top else None) + "\n"
            "asset_paths = " + json.dumps(asset_paths) + "\n"
            "nwb_assets = [path for path in asset_paths if path.lower().endswith('.nwb') or '*.nwb' in path.lower()]\n"
            "print(json.dumps({'selected_dataset': selected_dataset, 'nwb_asset_count': len(nwb_assets), 'asset_preview_count': len(asset_paths)}, indent=2))\n"
        ),
        _markdown_cell(
            "## Real data loading next step\n\n"
            "For DANDI/NWB candidates, install `dandi pynwb remfile` and open one concrete `.nwb` asset from the inventory. For OpenNeuro/BIDS candidates, install `mne` or modality-specific BIDS tooling and start from `dataset_description.json` plus subject folders."
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {"language_info": {"name": "python", "pygments_lexer": "ipython3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")


def _write_provenance(
    path: Path,
    question: str,
    query: QuerySpec,
    ranked: list[RankedCandidate],
    inspections: tuple[DatasetInspection, ...],
    offline: bool,
    execution_report: NotebookExecutionReport | None,
) -> None:
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
        "inspections": [_inspection_to_dict(item) for item in inspections],
        "execution": _execution_to_dict(execution_report),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_manifest(
    path: Path,
    question: str,
    ranked: list[RankedCandidate],
    inspections: tuple[DatasetInspection, ...],
    artifact_paths: list[Path],
    offline: bool,
    execution_report: NotebookExecutionReport | None,
) -> None:
    payload = {
        "question": question,
        "offline": offline,
        "artifact_count": len(artifact_paths),
        "artifacts": [artifact.name for artifact in artifact_paths],
        "top_dataset": _candidate_summary(ranked[0]) if ranked else None,
        "inspection": {"inspected_dataset_count": len(inspections)},
        "execution": _execution_to_dict(execution_report),
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


def _inspection_to_dict(item: DatasetInspection) -> dict[str, object]:
    return {
        "candidate_identifier": item.candidate_identifier,
        "asset_count": item.asset_count,
        "nwb_asset_count": item.nwb_asset_count,
        "bids_file_count": item.bids_file_count,
        "total_size_bytes": item.total_size_bytes,
        "standard_summary": item.standard_summary,
        "inferred_modalities": list(item.inferred_modalities),
        "representative_assets": [asset.path for asset in item.representative_assets],
        "warnings": list(item.warnings),
    }


def _execution_to_dict(report: NotebookExecutionReport | None) -> dict[str, object]:
    if report is None:
        return {"status": "not_requested"}
    return {
        "status": report.status,
        "backend": report.backend,
        "executed_cell_count": report.executed_cell_count,
        "reason": report.reason,
        "elapsed_seconds": report.elapsed_seconds,
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


def _inspection_markdown(inspection: DatasetInspection) -> str:
    return (
        f"- Asset preview count: {inspection.asset_count}\n"
        f"- NWB assets: {inspection.nwb_asset_count}\n"
        f"- BIDS-like files/directories: {inspection.bids_file_count}\n"
        f"- Inferred modalities: {_format_tuple(inspection.inferred_modalities)}\n"
    )


def _markdown_cell(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def _code_cell(source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source}


def _format_tuple(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "unknown"


def _format_size(value: int | None) -> str:
    if value is None:
        return "unknown"
    return str(value)


def _execution_security_note() -> str:
    return "Notebook execution uses a restricted local subprocess for generated notebook cells; it is useful for smoke verification but is not a hardened untrusted-code sandbox."
