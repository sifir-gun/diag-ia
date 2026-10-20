"""Doublures de test des ports. Aucune dépendance réseau."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.adapters.outbound.llm.fake import FakeAdviceGenerator
from app.adapters.outbound.persistence.memory import InMemoryDiagnosticRepository
from app.adapters.outbound.prompts import FilePromptProvider
from app.application.ports import AdviceGenerationError
from app.application.pricing import Pricing
from app.application.run_diagnostic import RunDiagnostic

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

VALID_ANSWERS = {
    "secteur": "Industrie manufacturière",
    "effectif": "10 à 49",
    "outils": ["Microsoft 365", "ERP", "Excel et fichiers partagés"],
    "taches": ["Devis et facturation", "Relances clients ou fournisseurs"],
    "heures": "20 à 50 heures",
    "donnees": "Dans des fichiers Excel structurés",
    "usage_ia": "Usage individuel (ChatGPT, Copilot…)",
    "competences": "Une personne à l’aise avec les outils",
    "budget": "5 000 à 15 000 €",
    "priorite": "Nos devis partent trop tard et on oublie de relancer.",
}


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 10, 20, 8, 0, 0, tzinfo=timezone.utc)


class SequentialIds:
    def __init__(self) -> None:
        self.n = 0

    def new_id(self) -> str:
        self.n += 1
        return f"diag-{self.n:04d}"


class RecordingEvents:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def publish(self, name: str, level: str = "INFO", **fields: object) -> None:
        self.events.append((name, level, fields))

    @property
    def names(self) -> list[str]:
        return [e[0] for e in self.events]


class BrokenRepository:
    def save(self, diagnostic):
        raise RuntimeError("BigQuery indisponible")

    def get(self, diagnostic_id):
        return None


class MalformedAdvisor:
    def generate(self, prompt, request):
        raise AdviceGenerationError("JSON du modèle invalide")


class CrashingAdvisor:
    def generate(self, prompt, request):
        raise ConnectionError("réseau coupé")


class CountingAdvisor(FakeAdviceGenerator):
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt, request):
        self.calls += 1
        return super().generate(prompt, request)


def make_use_case(*, advisor=None, repository=None, events=None):
    advisor = advisor or CountingAdvisor()
    repository = repository if repository is not None else InMemoryDiagnosticRepository()
    events = events or RecordingEvents()
    use_case = RunDiagnostic(
        advisor=advisor, repository=repository, prompts=FilePromptProvider(PROMPTS_DIR),
        events=events, clock=FixedClock(), ids=SequentialIds(),
        pricing=Pricing(1.50, 9.00), prompt_version="v1",
    )
    return use_case, advisor, repository, events
