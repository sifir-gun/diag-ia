"""Contrats HTTP. Ils traduisent le domaine, ils ne le remplacent pas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.model import Diagnostic


class DiagnosticRequest(BaseModel):
    answers: dict[str, str | list[str]]
    consent: bool
    contact_email: str | None = None


class RecommendationOut(BaseModel):
    title: str
    rationale: str
    estimated_gain: str
    effort: str
    confidence: float


class DiagnosticResponse(BaseModel):
    diagnostic_id: str
    created_at: datetime
    score: int
    score_breakdown: dict[str, int]
    maturity_label: str
    summary: str
    recommendations: list[RecommendationOut]
    model: str
    prompt_version: str
    record_sha256: str

    @classmethod
    def from_domain(cls, d: Diagnostic) -> "DiagnosticResponse":
        return cls(
            diagnostic_id=d.id,
            created_at=d.created_at,
            score=d.score.total,
            score_breakdown=dict(d.score.breakdown),
            maturity_label=d.score.label,
            summary=d.advice.summary,
            recommendations=[RecommendationOut(**vars(r)) for r in d.advice.recommendations],
            model=d.model,
            prompt_version=d.prompt.version,
            record_sha256=d.fingerprints.record_sha256,
        )
