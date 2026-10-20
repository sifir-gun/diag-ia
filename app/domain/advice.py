"""Règles sur le conseil produit par le modèle : on ne lui fait jamais confiance tel quel."""
from __future__ import annotations

import re
from dataclasses import replace

from app.domain.model import EFFORTS, Advice

MAX_RECOMMENDATIONS = 3

# Filet de sécurité : l'adaptateur du modèle doit avoir décodé les entités HTML.
HTML_ENTITY = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")


class InvalidAdvice(ValueError):
    """Le conseil reçu ne respecte pas le contrat."""


def _clean_text(text: str) -> str:
    if HTML_ENTITY.search(text):
        raise InvalidAdvice("Entité HTML non décodée dans le conseil")
    return text.strip().replace("'", "’")


def normalize_advice(advice: Advice) -> Advice:
    recommendations = []
    for rec in advice.recommendations[:MAX_RECOMMENDATIONS]:
        if rec.effort not in EFFORTS:
            raise InvalidAdvice(f"Effort inconnu : {rec.effort}")
        if not rec.title.strip() or not rec.rationale.strip():
            raise InvalidAdvice("Recommandation sans titre ou sans justification")
        recommendations.append(replace(
            rec,
            title=_clean_text(rec.title),
            rationale=_clean_text(rec.rationale),
            estimated_gain=_clean_text(rec.estimated_gain),
            confidence=round(min(max(float(rec.confidence), 0.0), 1.0), 2),
        ))
    if not recommendations or not advice.summary.strip():
        raise InvalidAdvice("Conseil incomplet")
    return Advice(summary=_clean_text(advice.summary), recommendations=tuple(recommendations))
