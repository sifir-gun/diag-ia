"""Cas d'usage principal : produire un diagnostic tracé.

Règle : aucun résultat n'est renvoyé sans avoir été enregistré.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Mapping

from app.application.errors import AdviceUnavailable, DiagnosticNotRecorded
from app.application.ports import (
    AdviceGenerationError, AdviceGenerator, AdviceRequest, AdviceTemporarilyUnavailable, Clock,
    DiagnosticRepository, EventPublisher, GeneratedAdvice, IdGenerator, Prompt, PromptProvider,
)
from app.application.pricing import Pricing
from app.application.retry import RetryPolicy
from app.domain.advice import InvalidAdvice, normalize_advice
from app.domain.fingerprint import compute_fingerprints
from app.domain.model import Diagnostic, Usage
from app.domain.scoring import compute_score
from app.domain.submission import validate_submission


@dataclass(frozen=True)
class RunDiagnosticCommand:
    answers: Mapping[str, object]
    consent: bool
    contact_email: str | None = None


class RunDiagnostic:
    def __init__(self, *, advisor: AdviceGenerator, repository: DiagnosticRepository,
                 prompts: PromptProvider, events: EventPublisher, clock: Clock,
                 ids: IdGenerator, pricing: Pricing, prompt_version: str, retry: RetryPolicy,
                 sleep: Callable[[float], None] = time.sleep,
                 monotonic: Callable[[], float] = time.monotonic):
        self._advisor = advisor
        self._repository = repository
        self._prompts = prompts
        self._events = events
        self._clock = clock
        self._ids = ids
        self._pricing = pricing
        self._prompt_version = prompt_version
        self._retry = retry
        self._sleep = sleep
        self._monotonic = monotonic

    def execute(self, command: RunDiagnosticCommand) -> Diagnostic:
        # Lève InvalidSubmission avant tout appel coûteux.
        submission = validate_submission(command.answers, consent=command.consent,
                                         contact_email=command.contact_email)
        diagnostic_id = self._ids.new_id()
        created_at = self._clock.now()
        prompt = self._prompts.load(self._prompt_version)
        score = compute_score(submission.answers)

        started = time.perf_counter()
        try:
            generated, attempts = self._generate(diagnostic_id, prompt,
                                                 AdviceRequest(submission.answers, score))
            advice = normalize_advice(generated.advice)
        except (AdviceGenerationError, InvalidAdvice) as exc:
            self._events.publish("advice_rejected", "WARNING",
                                 diagnostic_id=diagnostic_id, reason=str(exc)[:300])
            raise AdviceUnavailable("Conseil invalide") from exc
        except Exception as exc:
            self._events.publish("advice_failed", "ERROR",
                                 diagnostic_id=diagnostic_id, error=type(exc).__name__)
            raise AdviceUnavailable("Générateur indisponible") from exc
        latency_ms = int((time.perf_counter() - started) * 1000)

        diagnostic = Diagnostic(
            id=diagnostic_id,
            created_at=created_at,
            answers=submission.answers,
            score=score,
            advice=advice,
            prompt=prompt.ref,
            model=generated.model,
            usage=Usage(
                input_tokens=generated.input_tokens,
                output_tokens=generated.output_tokens,
                latency_ms=latency_ms,
                cost_usd=self._pricing.cost(generated.input_tokens, generated.output_tokens),
            ),
            fingerprints=compute_fingerprints(
                diagnostic_id=diagnostic_id, created_at=created_at,
                answers=submission.answers, score=score, advice=advice,
                prompt=prompt.ref, model=generated.model,
            ),
            contact_email=submission.contact_email,
        )

        try:
            self._repository.save(diagnostic)
        except Exception as exc:
            self._events.publish("storage_failed", "ERROR",
                                 diagnostic_id=diagnostic_id, error=type(exc).__name__)
            raise DiagnosticNotRecorded("Enregistrement impossible") from exc

        # L'e-mail du visiteur ne part jamais dans les événements.
        self._events.publish(
            "diagnostic_completed",
            diagnostic_id=diagnostic_id, score=score.total, model=generated.model,
            prompt_version=prompt.version, input_tokens=diagnostic.usage.input_tokens,
            output_tokens=diagnostic.usage.output_tokens, latency_ms=latency_ms,
            cost_usd=diagnostic.usage.cost_usd,
            record_sha256=diagnostic.fingerprints.record_sha256, attempts=attempts,
        )
        return diagnostic

    def _generate(self, diagnostic_id: str, prompt: Prompt,
                  request: AdviceRequest) -> tuple[GeneratedAdvice, int]:
        """Redemande le conseil après une erreur passagère, dans le budget de la politique."""
        started = self._monotonic()
        attempt = 1
        while True:
            try:
                return self._advisor.generate(prompt, request), attempt
            except AdviceTemporarilyUnavailable as exc:
                delay = self._retry.next_delay(attempt, self._monotonic() - started)
                if delay is None:
                    raise
                attempt += 1
                self._events.publish("advice_retry", "WARNING", diagnostic_id=diagnostic_id,
                                     attempt=attempt, reason=exc.reason, delay_s=delay)
                self._sleep(delay)
