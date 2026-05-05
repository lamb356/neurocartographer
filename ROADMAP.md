# Roadmap

NeuroCartographer's north star is trustworthy open-neurodata reuse: a researcher asks a neuroscience question and receives ranked datasets, inspected assets, executable starter analyses, and explicit caveats.

## v0.1 — committed baseline

- Plain-language query parsing.
- DANDI/offline candidate discovery.
- Transparent ranking.
- Dataset cards, QC report, starter notebook, provenance, and run manifest.
- Regression tests and packaging smoke.

## v0.2 — current build

- Publish public GitHub repository.
- GitHub Actions CI.
- DANDI asset inventory for ranked candidates.
- NWB metadata summary from inspected asset paths/sizes.
- More concrete NWB starter notebook cells.
- Restricted local execution report for generated notebooks.
- OpenNeuro/BIDS connector with metadata/file-tree parsing.

## v0.3 — next high-value milestone

- Real NWB metadata reads through optional `pynwb`/`remfile` when available.
- OpenNeuro recursive BIDS file-tree inspection.
- Analysis templates for NWB ophys, NWB ephys, BIDS EEG, and BIDS fMRI.
- CubeSandbox/E2B execution backend once credentials/template are configured.

## v1.0 bar

- Dataset search across DANDI, OpenNeuro, Allen, and IBL.
- Verified execution package with reproducible notebooks and provenance.
- Benchmark suite of neuroscience questions with expected data-source families.
- Strong documentation for contributors and scientific caveat policy.
