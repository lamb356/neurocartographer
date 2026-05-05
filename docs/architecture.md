# Architecture

NeuroCartographer is intentionally built as a small ports-and-adapters Python project.

```text
CLI
 -> pipeline use case
    -> query parser
    -> dataset connectors
       -> DANDI REST metadata/assets
       -> OpenNeuro GraphQL metadata/files
       -> offline seed catalog
    -> ranking policy
    -> asset/NWB/BIDS inspection
    -> artifact writers
    -> optional generated-notebook executor
```

## Core boundaries

- `query.py` — deterministic conversion from plain-language question to `QuerySpec`.
- `models.py` — framework-free data contracts for queries, candidates, assets, inspections, execution reports, and artifacts.
- `connectors/` — replaceable data-source adapters.
- `connectors/dandi.py` — DANDI search plus asset-preview parsing.
- `connectors/openneuro.py` — OpenNeuro/BIDS GraphQL metadata/file preview parsing.
- `connectors/static_catalog.py` — deterministic seed data for offline tests/demos.
- `ranking.py` — transparent dataset-fit scoring.
- `inspection.py` — asset-preview summarization and NWB/BIDS modality inference.
- `execution.py` — restricted local smoke execution for generated notebooks.
- `artifacts.py` — report/notebook/provenance generation.
- `pipeline.py` — application use case that orchestrates the full flow.
- `cli.py` — delivery mechanism only.

## Trust model

The system separates metadata evidence from scientific claims.

- Candidate ranking is a recommendation based on metadata/text matching.
- Asset inspection currently uses API metadata and file paths/sizes, not full data-array reads.
- Generated notebooks are starter scaffolds.
- `--execute-notebook` runs generated notebook code cells in a restricted local subprocess and writes `execution_report.json`.
- The restricted local executor is a smoke gate, not a hardened sandbox for arbitrary untrusted notebooks.
- Reports must mark unexecuted scientific conclusions as unknown.
- `provenance.json` records the claim policy, candidate ranking evidence, asset summaries, and execution status.

## Data surfaces

- Offline deterministic catalog: always available for tests and demos.
- DANDI API connector: unauthenticated HTTPS metadata search and asset preview.
- OpenNeuro API connector: unauthenticated GraphQL metadata and BIDS file preview.

## Extension points

Future connectors should implement the `DatasetConnector` protocol:

```python
class DatasetConnector(Protocol):
    name: str
    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]: ...
```

High-value next adapters/features:

- Allen Brain Observatory metadata search.
- International Brain Laboratory metadata search.
- Optional real NWB metadata reads through `pynwb`/`remfile`.
- Optional real BIDS inspection through modality-specific readers such as MNE.
- Hardened remote sandbox execution backend for untrusted/generated analysis beyond the current local smoke gate.
