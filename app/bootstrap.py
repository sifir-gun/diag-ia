"""Racine de composition : le seul endroit qui choisit les adaptateurs.

Changer de modèle, de base ou passer en mode local se fait ici, par la
configuration, sans toucher au domaine ni aux cas d'usage.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.adapters.outbound.llm.fake import FakeAdviceGenerator
from app.adapters.outbound.llm.gemini import GeminiAdviceGenerator
from app.adapters.outbound.observability import LoggingEventPublisher, configure_json_logging
from app.adapters.outbound.persistence.bigquery import BigQueryDiagnosticRepository
from app.adapters.outbound.persistence.memory import InMemoryDiagnosticRepository
from app.adapters.outbound.prompts import FilePromptProvider
from app.adapters.outbound.system import UtcClock, UuidIdGenerator
from app.application.ports import AdviceGenerator, DiagnosticRepository
from app.application.pricing import Pricing
from app.application.run_diagnostic import RunDiagnostic
from app.application.verify_diagnostic import VerifyDiagnostic
from app.config import Settings

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@dataclass(frozen=True)
class Container:
    run_diagnostic: RunDiagnostic
    verify_diagnostic: VerifyDiagnostic


def build_container(settings: Settings) -> Container:
    events = LoggingEventPublisher(configure_json_logging(settings.project))
    prompts = FilePromptProvider(PROMPTS_DIR)
    prompts.load(settings.prompt_version)  # échoue au démarrage plutôt qu'au premier visiteur

    advisor: AdviceGenerator
    if settings.llm_backend == "fake":
        advisor = FakeAdviceGenerator()
    else:
        advisor = GeminiAdviceGenerator(settings.project, settings.vertex_location, settings.gemini_model,
                                         settings.thinking_level)

    repository: DiagnosticRepository
    if settings.store_backend == "memory":
        repository = InMemoryDiagnosticRepository()
    else:
        repository = BigQueryDiagnosticRepository(settings.project, settings.bq_dataset, settings.bq_table)

    run = RunDiagnostic(
        advisor=advisor, repository=repository, prompts=prompts, events=events,
        clock=UtcClock(), ids=UuidIdGenerator(),
        pricing=Pricing(settings.price_input_usd_per_mtok, settings.price_output_usd_per_mtok),
        prompt_version=settings.prompt_version,
    )
    return Container(run_diagnostic=run, verify_diagnostic=VerifyDiagnostic(repository))
