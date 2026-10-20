"""Adaptateur BigQuery du port DiagnosticRepository."""
from __future__ import annotations

from app.adapters.outbound.persistence.rows import from_row, to_row
from app.domain.model import Diagnostic


class BigQueryDiagnosticRepository:
    def __init__(self, project: str, dataset: str, table: str):
        self._project = project
        self._table_id = f"{project}.{dataset}.{table}"
        self._client = None

    def _bq(self):
        if self._client is None:
            from google.cloud import bigquery
            self._client = bigquery.Client(project=self._project)
        return self._client

    def save(self, diagnostic: Diagnostic) -> None:
        errors = self._bq().insert_rows_json(self._table_id, [to_row(diagnostic)],
                                             row_ids=[diagnostic.id])
        if errors:
            raise RuntimeError(f"Insertion BigQuery refusée : {errors}")

    def get(self, diagnostic_id: str) -> Diagnostic | None:
        from google.cloud import bigquery

        job = self._bq().query(
            f"SELECT * FROM `{self._table_id}` WHERE diagnostic_id = @id LIMIT 1",
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", diagnostic_id)]
            ),
        )
        rows = list(job.result())
        return from_row(dict(rows[0].items())) if rows else None
