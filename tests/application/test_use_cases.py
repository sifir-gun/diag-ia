import pytest

from app.application.errors import AdviceUnavailable, DiagnosticNotRecorded
from app.application.run_diagnostic import RunDiagnosticCommand
from app.application.verify_diagnostic import VerificationStatus, VerifyDiagnostic
from app.domain.submission import InvalidSubmission
from tests.fakes import (
    VALID_ANSWERS, BrokenRepository, CrashingAdvisor, MalformedAdvisor, make_use_case,
)

COMMAND = RunDiagnosticCommand(answers=VALID_ANSWERS, consent=True, contact_email="dg@pme.fr")


def test_diagnostic_is_recorded_then_returned():
    use_case, advisor, repository, events = make_use_case()
    diagnostic = use_case.execute(COMMAND)
    assert diagnostic.id == "diag-0001"
    assert len(diagnostic.advice.recommendations) == 3
    assert diagnostic.usage.cost_usd > 0
    assert repository.get("diag-0001") == diagnostic
    assert events.names == ["diagnostic_completed"]


def test_contact_email_never_reaches_the_events():
    use_case, _, _, events = make_use_case()
    use_case.execute(COMMAND)
    assert "dg@pme.fr" not in repr(events.events)


def test_invalid_submission_stops_before_the_model():
    use_case, advisor, repository, _ = make_use_case()
    with pytest.raises(InvalidSubmission):
        use_case.execute(RunDiagnosticCommand(answers=VALID_ANSWERS, consent=False))
    assert advisor.calls == 0 and repository.rows == {}


@pytest.mark.parametrize("advisor, event", [
    (MalformedAdvisor(), "advice_rejected"),
    (CrashingAdvisor(), "advice_failed"),
])
def test_model_failure_records_nothing(advisor, event):
    use_case, _, repository, events = make_use_case(advisor=advisor)
    with pytest.raises(AdviceUnavailable):
        use_case.execute(COMMAND)
    assert repository.rows == {}
    assert events.names == [event]


def test_no_result_without_a_record():
    use_case, _, _, events = make_use_case(repository=BrokenRepository())
    with pytest.raises(DiagnosticNotRecorded):
        use_case.execute(COMMAND)
    assert events.names == ["storage_failed"]


def test_verification_detects_tampering_in_storage():
    use_case, _, repository, _ = make_use_case()
    diagnostic = use_case.execute(COMMAND)
    verify = VerifyDiagnostic(repository)
    assert verify.execute(diagnostic.id) is VerificationStatus.INTACT
    repository.rows[diagnostic.id]["score"] = 99
    assert verify.execute(diagnostic.id) is VerificationStatus.ALTERED
    assert verify.execute("inconnu") is VerificationStatus.NOT_FOUND
