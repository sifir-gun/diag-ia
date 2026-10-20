"""Fabrique de l'application FastAPI. Elle reçoit ses cas d'usage tout prêts."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.adapters.inbound.web import api, html
from app.adapters.shared.tracing import parse_trace_header, trace_id
from app.application.run_diagnostic import RunDiagnostic


def create_app(*, run_diagnostic: RunDiagnostic, contact_email: str = "") -> FastAPI:
    app = FastAPI(title="Diagnostic de maturité IA", version="2.0.0")
    app.state.run_diagnostic = run_diagnostic
    app.state.contact_email = contact_email
    app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")

    @app.middleware("http")
    async def cloud_trace_context(request: Request, call_next):
        token = trace_id.set(parse_trace_header(request.headers.get("x-cloud-trace-context")))
        try:
            return await call_next(request)
        finally:
            trace_id.reset(token)

    # Cloud Run réserve certains chemins finissant par « z » : on évite /healthz.
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(html.router)
    app.include_router(api.router)
    return app
