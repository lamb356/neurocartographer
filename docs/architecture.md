# Architecture

NeuroCartographer is intentionally built as a small ports-and-adapters Python project.

```text
CLI
 -> pipeline use case
    -> query parser
    -> dataset connectors
    -> ranking policy
    -> artifact writers
```

## Core boundaries

- `query.py` — deterministic conversion from plain-language question to `QuerySpec`.
- `models.py` — framework-free data contracts.
- `connectors/` — replaceable data-source adapters.
- `ranking.py` — transparent dataset-fit scoring.
- `artifacts.py` — report/notebook/provenance generation.
- `pipeline.py` — application use case that orchestrates the full flow.
- `cli.py` — delivery mechanism only.

## Trust model

The system separates metadata evidence from scientific claims.

- Candidate ranking is a recommendation based on metadata/text matching.
- Generated notebooks are starter scaffolds.
- Reports must mark unexecuted scientific conclusions as unknown.
- `provenance.json` records the claim policy and candidate ranking evidence.

## v0.1 data surfaces

- Offline deterministic catalog: always available for tests and demos.
- DANDI API connector: unauthenticated HTTPS metadata search.

## Extension points

Future connectors should implement the `DatasetConnector` protocol:

```python
class DatasetConnector(Protocol):
    name: str
    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]: ...
```

Future high-value adapters:

- OpenNeuro/BIDS metadata search.
- Allen Brain Observatory metadata search.
- International Brain Laboratory metadata search.
- Actual NWB/BIDS asset inspection and notebook execution in a sandbox.
