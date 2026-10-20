"""Adaptateur mémoire du port DiagnosticRepository.

Il stocke des lignes, pas des objets : la traduction vers BigQuery est donc
testée à chaque test.
"""
from __future__ import annotations

from typing import Any

from app.adapters.outbound.persistence.rows import from_row, to_row
from app.domain.model import Diagnostic


class InMemoryDiagnosticRepository:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}

    def save(self, diagnostic: Diagnostic) -> None:
        self.rows[diagnostic.id] = to_row(diagnostic)

    def get(self, diagnostic_id: str) -> Diagnostic | None:
        row = self.rows.get(diagnostic_id)
        return from_row(row) if row else None
