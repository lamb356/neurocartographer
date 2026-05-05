# NeuroCartographer Goal

## Mission

NeuroCartographer turns a plain-language neuroscience question into a verified, reproducible open-neurodata reuse package.

The v0.1 product focuses on the highest-value wedge:

```text
scientific question -> dataset search -> dataset fit ranking -> executable starter notebook -> dataset/reproducibility reports -> provenance manifest
```

## Directional thesis

Open neuroscience does not primarily lack data or Python libraries. It lacks a trustworthy AI-native reuse layer that helps researchers discover which public datasets can answer a question, generates the first analysis scaffold, and records exactly what was verified versus inferred.

## v0.1 scope

### In scope

- DANDI/NWB-first dataset discovery.
- Offline deterministic fallback catalog so the project works without credentials or network.
- Plain-language question parsing into a query spec.
- Dataset candidate ranking with transparent scoring reasons.
- Reproducible artifact generation:
  - `dataset_cards.md`
  - `qc_report.md`
  - `starter_analysis.ipynb`
  - `provenance.json`
  - `run_manifest.json`
- CLI entrypoint usable from a fresh checkout.
- Tests covering search/ranking/report/notebook/CLI paths.

### Out of scope for v0.1

- Clinical diagnosis or medical advice.
- Claims about scientific results unless code actually computes them.
- Training a brain foundation model.
- Heavy local downloads by default.
- Requiring DANDI/OpenNeuro credentials.

## Trust contract

NeuroCartographer may recommend candidate datasets and generate analysis scaffolds. It must not claim scientific findings unless the relevant computation was executed and the output is captured in provenance.

Every generated report should distinguish:

- `verified`: known from explicit metadata or generated artifact validation.
- `inferred`: derived from heuristic ranking or text matching.
- `unknown`: not found in available metadata.

## Completion definition for this first build

The first build is complete when a user can run from a source checkout:

```bash
PYTHONPATH=src python -m neurocartographer "Find mouse visual cortex calcium imaging datasets with behavior" --offline --out runs/demo
```

or, after installation:

```bash
neurocartographer "Find mouse visual cortex calcium imaging datasets with behavior" --offline --out runs/demo
```

and get a tested artifact package with ranked datasets, a starter notebook, provenance, and a manifest without network access or secrets.
