import json
from datetime import datetime

from app.adapters.outbound.persistence.rows import from_row, to_row
from app.application.run_diagnostic import RunDiagnosticCommand
from app.domain.fingerprint import verify
from tests.fakes import VALID_ANSWERS, make_use_case


def test_row_round_trip_as_bigquery_returns_it():
    """BigQuery renvoie les colonnes JSON décodées et les dates en datetime."""
    use_case, *_ = make_use_case()
    diagnostic = use_case.execute(RunDiagnosticCommand(answers=VALID_ANSWERS, consent=True))
    row = to_row(diagnostic)
    as_read = {**row,
               "created_at": datetime.fromisoformat(row["created_at"]),
               "answers": json.loads(row["answers"]),
               "score_breakdown": json.loads(row["score_breakdown"]),
               "recommendations": json.loads(row["recommendations"])}
    restored = from_row(as_read)
    assert restored == diagnostic
    assert verify(restored)
