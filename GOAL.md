# NeuroCartographer Goal

## Mission

NeuroCartographer turns a plain-language neuroscience question into a verified, reproducible open-neurodata reuse package.

The current v0.2 product wedge is:

```text
scientific question
-> dataset search across DANDI/OpenNeuro/offline seeds
-> transparent dataset-fit ranking
-> DANDI/OpenNeuro asset preview inspection
-> NWB/BIDS metadata summary
-> concrete starter notebook
-> optional generated-notebook smoke execution
-> dataset/reproducibility reports
-> provenance manifest
```

## Directional thesis

Open neuroscience does not primarily lack data or Python libraries. It lacks a trustworthy AI-native reuse layer that helps researchers discover which public datasets can answer a question, generates the first analysis scaffold, and records exactly what was verified versus inferred.

## Current scope

### In scope

- DANDI/NWB dataset discovery through public unauthenticated metadata APIs.
- OpenNeuro/BIDS dataset discovery through the public unauthenticated GraphQL API.
- Offline deterministic fallback catalog so the project works without credentials or network.
- Plain-language question parsing into a query spec.
- Dataset candidate ranking with transparent scoring reasons.
- Asset preview inspection for ranked candidates.
- NWB/BIDS summary from metadata and asset paths.
- Reproducible artifact generation:
  - `dataset_cards.md`
  - `qc_report.md`
  - `starter_analysis.ipynb`
  - `asset_inventory.md`
  - `nwb_summary.md`
  - `execution_report.json` when `--execute-notebook` is used
  - `provenance.json`
  - `run_manifest.json`
- CLI entrypoint usable from a fresh checkout or installed package.
- GitHub Actions CI.
- Tests covering search/ranking/report/notebook/CLI/execution paths.

### Out of scope for the current version

- Clinical diagnosis or medical advice.
- Claims about scientific results unless code actually computes them.
- Training a brain foundation model.
- Heavy local downloads by default.
- Requiring DANDI/OpenNeuro credentials.
- Treating the restricted local notebook smoke executor as a hardened untrusted-code sandbox.

## Trust contract

NeuroCartographer may recommend candidate datasets and generate analysis scaffolds. It must not claim scientific findings unless the relevant computation was executed and the output is captured in provenance.

Every generated report should distinguish:

- `verified`: known from explicit metadata, generated artifact validation, or generated-notebook smoke execution.
- `inferred`: derived from heuristic ranking, metadata, or asset-path matching.
- `unknown`: not found in available metadata.

## Completion definition for the current build

The build is complete when a user can run from a source checkout:

```bash
PYTHONPATH=src python -m neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --execute-notebook \
  --out runs/demo
```

or, after installation:

```bash
neurocartographer \
  "Find mouse visual cortex calcium imaging datasets with behavior" \
  --offline \
  --execute-notebook \
  --out runs/demo
```

and get a tested artifact package with ranked datasets, asset inventory, NWB/BIDS summary, a starter notebook, generated-notebook execution report, provenance, and a manifest without network access or secrets.
