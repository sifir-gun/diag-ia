"""Règles sur le conseil produit par le modèle : on ne lui fait jamais confiance tel quel."""
from __future__ import annotations

from dataclasses import replace

from app.domain.model import EFFORTS, Advice

MAX_RECOMMENDATIONS = 3


class InvalidAdvice(ValueError):
    """Le conseil reçu ne respecte pas le contrat."""


def normalize_advice(advice: Advice) -> Advice:
    recommendations = []
    for rec in advice.recommendations[:MAX_RECOMMENDATIONS]:
        if rec.effort not in EFFORTS:
            raise InvalidAdvice(f"Effort inconnu : {rec.effort}")
        if not rec.title.strip() or not rec.rationale.strip():
            raise InvalidAdvice("Recommandation sans titre ou sans justification")
        recommendations.append(replace(
            rec,
            title=rec.title.strip(),
            rationale=rec.rationale.strip(),
            confidence=round(min(max(float(rec.confidence), 0.0), 1.0), 2),
        ))
    if not recommendations or not advice.summary.strip():
        raise InvalidAdvice("Conseil incomplet")
    return Advice(summary=advice.summary.strip(), recommendations=tuple(recommendations))
