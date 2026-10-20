"""Entrée web pour les machines : API JSON."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.adapters.inbound.web.schemas import DiagnosticRequest, DiagnosticResponse
from app.application.errors import AdviceUnavailable, DiagnosticNotRecorded
from app.application.run_diagnostic import RunDiagnosticCommand
from app.domain.submission import InvalidSubmission

router = APIRouter(prefix="/api")


@router.post("/diagnostic", response_model=DiagnosticResponse)
def create_diagnostic(payload: DiagnosticRequest, request: Request):
    command = RunDiagnosticCommand(answers=payload.answers, consent=payload.consent,
                                   contact_email=payload.contact_email)
    try:
        diagnostic = request.app.state.run_diagnostic.execute(command)
    except InvalidSubmission as exc:
        raise HTTPException(422, detail=exc.errors) from exc
    except AdviceUnavailable as exc:
        raise HTTPException(502, detail="L’analyse n’a pas abouti.") from exc
    except DiagnosticNotRecorded as exc:
        raise HTTPException(503, detail="Le diagnostic n’a pas pu être enregistré.") from exc
    return DiagnosticResponse.from_domain(diagnostic)
