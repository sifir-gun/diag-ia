"""Entrée en ligne de commande : vérifier l'intégrité d'un diagnostic."""
from __future__ import annotations

from app.application.verify_diagnostic import VerificationStatus, VerifyDiagnostic

MESSAGES = {
    VerificationStatus.INTACT: (0, "Intègre : les trois empreintes correspondent."),
    VerificationStatus.ALTERED: (1, "Altéré : au moins une empreinte ne correspond plus."),
    VerificationStatus.NOT_FOUND: (2, "Diagnostic introuvable."),
}


def run(verify: VerifyDiagnostic, diagnostic_id: str) -> int:
    code, message = MESSAGES[verify.execute(diagnostic_id)]
    print(message)
    return code
