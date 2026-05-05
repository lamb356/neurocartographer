# NeuroCartographer

Open-source AI-native infrastructure for turning plain-language neuroscience questions into reproducible open-neurodata starter analyses.

## Install for development

This project has no runtime dependencies for v0.1.

```bash
python -m pip install -e .
```

If you do not want to install it yet, run from the source tree with:

```bash
PYTHONPATH=src python -m neurocartographer "Find mouse visual cortex calcium imaging datasets with behavior" --offline --out runs/demo
```

## v0.1 command

```bash
neurocartographer "Find mouse visual cortex calcium imaging datasets with behavior" --offline --out runs/demo
```

Generated artifacts:

- `dataset_cards.md` — ranked candidate datasets and fit reasons.
- `qc_report.md` — what was verified, inferred, and still unknown.
- `starter_analysis.ipynb` — a starter notebook scaffold.
- `provenance.json` — machine-readable provenance.
- `run_manifest.json` — run summary and artifact paths.

## Test

```bash
python -m pytest
```

## Design principles

1. No scientific claim without executed evidence.
2. Work offline by default for demos/tests.
3. Prefer open standards: DANDI/NWB first, BIDS/OpenNeuro later.
4. Make ranking reasons explicit and auditable.
5. Keep connectors replaceable and core ranking/report logic testable.

See:

- `GOAL.md`
- `docs/architecture.md`
- `docs/acceptance.md`
