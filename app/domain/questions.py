"""Les 10 questions du diagnostic et la validation des réponses."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

TEXT_MAX = 600


@dataclass(frozen=True)
class Question:
    key: str
    label: str
    kind: str  # "single", "multi" ou "text"
    options: tuple[str, ...] = ()
    help: str = ""


QUESTIONS: tuple[Question, ...] = (
    Question("secteur", "Votre secteur d’activité", "single", (
        "Industrie manufacturière", "BTP", "Commerce et distribution",
        "Services aux entreprises", "Finance et assurance",
        "Transport et logistique", "Santé", "Autre",
    )),
    Question("effectif", "Nombre de salariés", "single", (
        "1 à 9", "10 à 49", "50 à 249", "250 et plus",
    )),
    Question("outils", "Les outils que vous utilisez au quotidien", "multi", (
        "Microsoft 365", "Google Workspace", "ERP", "CRM",
        "Logiciel métier spécifique", "Excel et fichiers partagés",
        "Outil de gestion de tâches",
    ), help="Plusieurs choix possibles."),
    Question("taches", "Les tâches répétitives qui vous coûtent le plus de temps", "multi", (
        "Saisie et ressaisie de données", "Devis et facturation",
        "Relances clients ou fournisseurs", "Tri et réponse aux e-mails",
        "Reporting et tableaux de bord", "Planification",
        "Recherche d’informations dans des documents",
    ), help="Plusieurs choix possibles."),
    Question("heures", "Temps passé sur ces tâches chaque semaine, toutes personnes confondues", "single", (
        "Moins de 5 heures", "5 à 20 heures", "20 à 50 heures", "Plus de 50 heures",
    )),
    Question("donnees", "Où se trouvent vos données", "single", (
        "Dans un ERP ou un CRM bien tenu", "Dans des fichiers Excel structurés",
        "Éparpillées entre e-mails, PDF et papier", "Je ne sais pas",
    )),
    Question("usage_ia", "Votre usage actuel de l’IA", "single", (
        "Aucun", "Usage individuel (ChatGPT, Copilot…)",
        "Quelques automatisations en place", "Des projets IA en production",
    )),
    Question("competences", "Les compétences numériques en interne", "single", (
        "Personne en interne", "Une personne à l’aise avec les outils",
        "Une équipe informatique",
    )),
    Question("budget", "Budget envisagé pour un premier projet", "single", (
        "Moins de 5 000 €", "5 000 à 15 000 €", "15 000 à 50 000 €",
        "Plus de 50 000 €", "Pas encore défini",
    )),
    Question("priorite", "Si vous ne deviez régler qu’un seul problème cette année, lequel ?", "text",
             help="Quelques phrases suffisent."),
)

QUESTIONS_BY_KEY = {q.key: q for q in QUESTIONS}


def validate_answers(raw: Mapping[str, object]) -> tuple[dict[str, object], dict[str, str]]:
    """Renvoie les réponses normalisées et les erreurs, question par question."""
    clean: dict[str, object] = {}
    errors: dict[str, str] = {}
    for q in QUESTIONS:
        value = raw.get(q.key)
        if q.kind == "single":
            if not isinstance(value, str) or value not in q.options:
                errors[q.key] = "Choisissez une réponse."
                continue
            clean[q.key] = value
        elif q.kind == "multi":
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, (list, tuple)) or not value:
                errors[q.key] = "Choisissez au moins une réponse."
                continue
            if any(v not in q.options for v in value):
                errors[q.key] = "Une des réponses n’est pas reconnue."
                continue
            clean[q.key] = [o for o in q.options if o in value]
        else:
            text = value.strip() if isinstance(value, str) else ""
            if len(text) < 5:
                errors[q.key] = "Décrivez votre priorité en quelques mots."
                continue
            clean[q.key] = text[:TEXT_MAX]
    return clean, errors
