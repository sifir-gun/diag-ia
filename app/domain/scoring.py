"""Score de maturité : une grille fixe, reproductible et explicable."""
from __future__ import annotations

from typing import Mapping

from app.domain.model import Score

WEIGHTS: dict[str, dict[str, int]] = {
    "donnees": {
        "Dans un ERP ou un CRM bien tenu": 30,
        "Dans des fichiers Excel structurés": 20,
        "Éparpillées entre e-mails, PDF et papier": 5,
        "Je ne sais pas": 0,
    },
    "usage_ia": {
        "Aucun": 0,
        "Usage individuel (ChatGPT, Copilot…)": 10,
        "Quelques automatisations en place": 20,
        "Des projets IA en production": 30,
    },
    "competences": {
        "Personne en interne": 0,
        "Une personne à l’aise avec les outils": 10,
        "Une équipe informatique": 20,
    },
}
TOOL_POINTS = 4
TOOL_CAP = 20
UNSTRUCTURED_TOOLS = {"Excel et fichiers partagés"}

PARTS = (
    ("donnees", "Organisation des données", 30),
    ("usage_ia", "Usage actuel de l’IA", 30),
    ("competences", "Compétences en interne", 20),
    ("outils", "Outillage numérique", 20),
)

LEVELS = ((75, "Avancé"), (50, "En structuration"), (25, "En démarrage"), (0, "Débutant"))


def maturity_label(total: int) -> str:
    for threshold, label in LEVELS:
        if total >= threshold:
            return label
    return LEVELS[-1][1]


def compute_score(answers: Mapping[str, object]) -> Score:
    breakdown = {key: WEIGHTS[key][answers[key]] for key in WEIGHTS}  # type: ignore[index]
    tools = [t for t in answers["outils"] if t not in UNSTRUCTURED_TOOLS]  # type: ignore[union-attr]
    breakdown["outils"] = min(len(tools) * TOOL_POINTS, TOOL_CAP)
    total = sum(breakdown.values())
    return Score(total=total, breakdown=breakdown, label=maturity_label(total))


def describe_breakdown(breakdown: Mapping[str, int]) -> list[dict[str, object]]:
    return [{"label": label, "points": breakdown.get(key, 0), "max": maximum}
            for key, label, maximum in PARTS]
