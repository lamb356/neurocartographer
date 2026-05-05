from __future__ import annotations

from typing import Protocol

from neurocartographer.models import DatasetCandidate, QuerySpec


class DatasetConnector(Protocol):
    name: str

    def search(self, query: QuerySpec, limit: int) -> list[DatasetCandidate]:
        """Return candidate datasets for a parsed query."""
