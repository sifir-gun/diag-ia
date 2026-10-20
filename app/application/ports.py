"""Ports de sortie : ce dont les cas d'usage ont besoin, sans dire comment c'est fait.

Chaque port a au moins deux adaptateurs : un réel (Google Cloud) et un local
(mémoire, faux modèle), ce qui permet de tester tout le cœur sans réseau.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol

from app.domain.model import Advice, Diagnostic, PromptRef, Score


@dataclass(frozen=True)
class Prompt:
    version: str
    text: str
    sha256: str

    @property
    def ref(self) -> PromptRef:
        return PromptRef(version=self.version, sha256=self.sha256)


@dataclass(frozen=True)
class AdviceRequest:
    answers: Mapping[str, object]
    score: Score


@dataclass(frozen=True)
class GeneratedAdvice:
    advice: Advice
    model: str
    input_tokens: int
    output_tokens: int


class AdviceGenerationError(RuntimeError):
    """Le générateur a répondu, mais pas dans le format attendu."""


class AdviceTemporarilyUnavailable(RuntimeError):
    """Générateur saturé ou trop lent (503, 429, délai dépassé) : un nouvel essai peut réussir."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class AdviceGenerator(Protocol):
    def generate(self, prompt: Prompt, request: AdviceRequest) -> GeneratedAdvice: ...


class DiagnosticRepository(Protocol):
    def save(self, diagnostic: Diagnostic) -> None: ...

    def get(self, diagnostic_id: str) -> Diagnostic | None: ...


class PromptProvider(Protocol):
    def load(self, version: str) -> Prompt: ...


class EventPublisher(Protocol):
    def publish(self, name: str, level: str = "INFO", **fields: object) -> None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class IdGenerator(Protocol):
    def new_id(self) -> str: ...
