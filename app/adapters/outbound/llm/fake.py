"""Générateur factice : développement local et tests, sans réseau."""
from __future__ import annotations

from app.adapters.outbound.llm.rendering import build_user_content
from app.application.ports import AdviceRequest, GeneratedAdvice, Prompt
from app.domain.model import Advice, Recommendation


class FakeAdviceGenerator:
    model = "fake-model"

    def generate(self, prompt: Prompt, request: AdviceRequest) -> GeneratedAdvice:
        advice = Advice(
            summary=("Diagnostic de démonstration, généré sans appel au modèle. "
                     "Vos tâches répétitives offrent un gisement de temps important."),
            recommendations=(
                Recommendation("Automatiser les relances de devis",
                               "Vos devis sont déjà suivis dans un fichier, ce qui rend la relance simple à automatiser.",
                               "3 à 5 heures par semaine", "faible", 0.8),
                Recommendation("Trier automatiquement les e-mails entrants",
                               "Le tri des e-mails fait partie de vos tâches les plus chronophages.",
                               "2 à 4 heures par semaine", "moyen", 0.65),
                Recommendation("Centraliser les données clients",
                               "Des données éparpillées limitent toute automatisation plus ambitieuse.",
                               "Prérequis aux projets suivants", "élevé", 0.5),
            ),
        )
        content = build_user_content(request)
        return GeneratedAdvice(advice=advice, model=self.model,
                               input_tokens=(len(prompt.text) + len(content)) // 4, output_tokens=350)
