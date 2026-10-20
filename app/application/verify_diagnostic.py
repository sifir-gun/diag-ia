"""Cas d'usage d'audit : un diagnostic stocké a-t-il été modifié ?"""
from __future__ import annotations

from enum import Enum

from app.application.ports import DiagnosticRepository
from app.domain.fingerprint import verify


class VerificationStatus(Enum):
    INTACT = "intact"
    ALTERED = "altered"
    NOT_FOUND = "not_found"


class VerifyDiagnostic:
    def __init__(self, repository: DiagnosticRepository):
        self._repository = repository

    def execute(self, diagnostic_id: str) -> VerificationStatus:
        diagnostic = self._repository.get(diagnostic_id)
        if diagnostic is None:
            return VerificationStatus.NOT_FOUND
        return VerificationStatus.INTACT if verify(diagnostic) else VerificationStatus.ALTERED
