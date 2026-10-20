"""Une soumission recevable : réponses valides, accord donné, e-mail correct."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

from app.domain.questions import validate_answers

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


@dataclass(frozen=True)
class Submission:
    answers: Mapping[str, object]
    contact_email: str | None


class InvalidSubmission(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Soumission invalide")
        self.errors = errors


def validate_submission(raw_answers: Mapping[str, object], *, consent: bool,
                        contact_email: str | None) -> Submission:
    answers, errors = validate_answers(raw_answers)
    if not consent:
        errors["consent"] = "Votre accord est nécessaire pour analyser vos réponses."
    email = (contact_email or "").strip()
    if email and not EMAIL_RE.fullmatch(email):
        errors["contact_email"] = "Cette adresse e-mail n’est pas valide."
    if errors:
        raise InvalidSubmission(errors)
    return Submission(answers=answers, contact_email=email or None)
