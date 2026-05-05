from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurocartographer.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="neurocartographer",
        description="Find open neuroscience datasets and generate a reproducible starter-analysis package.",
    )
    parser.add_argument("question", help="Plain-language neuroscience data reuse question.")
    parser.add_argument("--out", default="runs/latest", help="Output directory for generated artifacts.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum ranked candidates to keep.")
    parser.add_argument("--offline", action="store_true", help="Use deterministic built-in catalog only; no network calls.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(args.question, Path(args.out), offline=args.offline, limit=args.limit)
    except Exception as exc:
        parser.exit(2, f"neurocartographer: error: {exc}\n")

    top = result.ranked_candidates[0] if result.ranked_candidates else None
    summary = {
        "question": result.question,
        "output_dir": str(result.output_dir),
        "top_dataset": top.candidate.identifier if top else None,
        "top_score": top.score if top else None,
        "artifact_paths": [str(path) for path in result.artifact_paths],
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"NeuroCartographer wrote {len(result.artifact_paths)} artifacts to {result.output_dir}")
        if top:
            print(f"Top dataset: {top.candidate.identifier} — {top.candidate.title} (score {top.score})")
        print("Artifacts:")
        for path in result.artifact_paths:
            print(f"- {path}")
    return 0
