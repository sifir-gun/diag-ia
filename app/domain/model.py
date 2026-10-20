"""Entités et objets-valeurs du diagnostic."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

EFFORTS = ("faible", "moyen", "élevé")


@dataclass(frozen=True)
class Recommendation:
    title: str
    rationale: str
    estimated_gain: str
    effort: str
    confidence: float


@dataclass(frozen=True)
class Advice:
    """Ce que le modèle d'IA apporte : une synthèse et des recommandations."""
    summary: str
    recommendations: tuple[Recommendation, ...]


@dataclass(frozen=True)
class Score:
    """Calculé par une grille fixe, jamais par le modèle."""
    total: int
    breakdown: Mapping[str, int]
    label: str


@dataclass(frozen=True)
class PromptRef:
    version: str
    sha256: str


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float


@dataclass(frozen=True)
class Fingerprints:
    input_sha256: str
    output_sha256: str
    record_sha256: str


@dataclass(frozen=True)
class Diagnostic:
    id: str
    created_at: datetime
    answers: Mapping[str, object]
    score: Score
    advice: Advice
    prompt: PromptRef
    model: str
    usage: Usage
    fingerprints: Fingerprints
    contact_email: str | None = None
