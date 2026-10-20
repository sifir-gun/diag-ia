"""Entrée web pour les humains : formulaire et page de résultat."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from app.adapters.inbound.web.schemas import DiagnosticResponse
from app.application.errors import AdviceUnavailable, DiagnosticNotRecorded
from app.application.run_diagnostic import RunDiagnosticCommand
from app.domain.questions import QUESTIONS
from app.domain.scoring import describe_breakdown
from app.domain.submission import InvalidSubmission

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "questions": QUESTIONS, "values": {}, "errors": {}, "consent": False, "email": "",
    })


@router.post("/diagnostic", response_class=HTMLResponse)
async def submit(request: Request):
    form = await request.form()
    raw = {q.key: (form.getlist(q.key) if q.kind == "multi" else form.get(q.key)) for q in QUESTIONS}
    consent = form.get("consent") == "on"
    email = str(form.get("contact_email") or "").strip()
    command = RunDiagnosticCommand(answers=raw, consent=consent, contact_email=email or None)

    try:
        diagnostic = await run_in_threadpool(request.app.state.run_diagnostic.execute, command)
    except InvalidSubmission as exc:
        return templates.TemplateResponse(request, "index.html", {
            "questions": QUESTIONS, "values": raw, "errors": exc.errors,
            "consent": consent, "email": email,
        }, status_code=422)
    except AdviceUnavailable:
        return _error(request, 502, "L’analyse n’a pas abouti. Vos réponses n’ont pas été enregistrées : réessayez dans un instant.")
    except DiagnosticNotRecorded:
        return _error(request, 503, "Le diagnostic n’a pas pu être enregistré, il n’est donc pas affiché. Réessayez dans un instant.")

    result = DiagnosticResponse.from_domain(diagnostic)
    return templates.TemplateResponse(request, "result.html", {
        "r": result,
        "breakdown": describe_breakdown(result.score_breakdown),
        "contact_email": request.app.state.contact_email,
    })


def _error(request: Request, status: int, message: str):
    return templates.TemplateResponse(request, "error.html", {"message": message}, status_code=status)
