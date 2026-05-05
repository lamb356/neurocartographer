# NeuroCartographer

Open-source AI-native infrastructure for turning plain-language neuroscience questions into reproducible open-neurodata starter analyses.

NeuroCartographer's trust rule is simple: **no scientific claim without executed evidence**. It can rank and inspect datasets, generate starter notebooks, and smoke-run generated notebooks, but it does not claim biological results until real analysis cells execute successfully on real data arrays.

## Install for development

This project uses the Python standard library at runtime for the current core. Tests use `pytest`.

```bash
python -m pip install -e .
python -m pip install pytest
```

If you do not want to install it yet, run from the source tree with:

```bash
PYTHONPATH=src python -m neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --execute-notebook \
  --out runs/demo
```

## Command

```bash
neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --execute-notebook \
  --out runs/demo
```

Useful flags:

- `--offline` — use deterministic built-in catalog only; no network calls.
- `--execute-notebook` — smoke-run generated notebook cells in a restricted local subprocess and write `execution_report.json`.
- `--limit N` — keep the top N ranked candidates after ranking.
- `--json` — print a machine-readable summary.

Generated artifacts:

- `dataset_cards.md` — ranked candidate datasets and fit reasons.
- `qc_report.md` — what was verified, inferred, and still unknown.
- `starter_analysis.ipynb` — a concrete starter notebook scaffold.
- `asset_inventory.md` — inspected asset/file previews.
- `nwb_summary.md` — NWB/BIDS counts and inferred modalities.
- `execution_report.json` — generated-notebook execution result when requested.
- `provenance.json` — machine-readable provenance.
- `run_manifest.json` — run summary and artifact paths.

## Data sources

Current connectors:

- DANDI/NWB via the public unauthenticated DANDI REST API.
- OpenNeuro/BIDS via the public unauthenticated OpenNeuro GraphQL API.
- Deterministic offline seed catalog for tests and demos.

## Test

```bash
python -m pytest
```

## Design principles

1. No scientific claim without executed evidence.
2. Work offline for deterministic demos/tests.
3. Prefer open standards: DANDI/NWB and OpenNeuro/BIDS.
4. Make ranking reasons explicit and auditable.
5. Keep connectors replaceable and core ranking/report logic testable.
6. Treat generated-notebook local execution as a smoke check, not a hardened untrusted-code sandbox.

See:

- `GOAL.md`
- `ROADMAP.md`
- `docs/architecture.md`
- `docs/acceptance.md`
