# Acceptance checks

## Offline end-to-end demo with generated-notebook execution

```bash
PYTHONPATH=src python -m neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --execute-notebook \
  --out runs/demo \
  --limit 3 \
  --json
```

Expected:

- exits `0`
- top dataset is `DANDI:000728`
- writes eight artifacts:
  - `dataset_cards.md`
  - `qc_report.md`
  - `starter_analysis.ipynb`
  - `asset_inventory.md`
  - `nwb_summary.md`
  - `execution_report.json`
  - `provenance.json`
  - `run_manifest.json`
- `run_manifest.json` has `execution.status == "passed"`

## Test suite

```bash
python -m pytest
```

Expected:

```text
24 passed
```

## Packaging smoke

```bash
tmpdir=$(mktemp -d)
python -m pip install --no-deps --target "$tmpdir" .
PYTHONPATH="$tmpdir" python -m neurocartographer \
  "human EEG resting state dataset" \
  --offline \
  --execute-notebook \
  --out /tmp/neurocartographer-pack-smoke \
  --limit 2 \
  --json
```

Expected:

- exits `0`
- imports from installed package target rather than source tree
- top dataset is `OpenNeuro:ds004504`
- writes the eight artifact files

## Live metadata smoke

```bash
PYTHONPATH=src python -m neurocartographer \
  "mouse visual cortex calcium imaging behavior" \
  --execute-notebook \
  --out /tmp/neurocartographer-live-smoke \
  --limit 2 \
  --json
```

Expected:

- exits `0`
- uses DANDI/OpenNeuro APIs if available
- falls back to deterministic static catalog only when live connectors are unreachable
- writes asset inventory, NWB/BIDS summary, generated notebook, execution report, provenance, and manifest

## GitHub publication / CI

Expected:

- repository exists at `https://github.com/lamb356/neurocartographer`
- `.github/workflows/test.yml` runs pytest, an offline CLI smoke, and an installed-target package smoke on Python 3.11 and 3.12
- pushed commits on `main` receive GitHub Actions test runs
