# Acceptance checks

## Offline end-to-end demo

```bash
PYTHONPATH=src python -m neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --out runs/demo \
  --limit 3 \
  --json
```

Expected:

- exits `0`
- top dataset is `DANDI:000728`
- writes exactly five artifacts:
  - `dataset_cards.md`
  - `qc_report.md`
  - `starter_analysis.ipynb`
  - `provenance.json`
  - `run_manifest.json`

## Test suite

```bash
python -m pytest
```

Expected:

```text
6 passed
```

## Packaging smoke

```bash
tmpdir=$(mktemp -d)
python -m pip install --no-deps --target "$tmpdir" .
PYTHONPATH="$tmpdir" python -m neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --out /tmp/neurocartographer-pack-smoke \
  --limit 2 \
  --json
```

Expected:

- exits `0`
- imports from installed package target rather than source tree
- writes the five artifact files

## Live metadata smoke

```bash
PYTHONPATH=src python -m neurocartographer \
  "mouse visual cortex calcium imaging behavior" \
  --out /tmp/neurocartographer-live-smoke \
  --limit 2 \
  --json
```

Expected:

- exits `0`
- uses DANDI API if available
- falls back to deterministic static catalog if DANDI is unreachable
