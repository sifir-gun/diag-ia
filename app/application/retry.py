"""Règle de produit : combien de fois, et pendant combien de temps, redemander un conseil."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """Au plus 3 essais, attente croissante, et jamais plus de `budget_s` d'attente pour le visiteur.

    `attempt_timeout_s` est le délai maximal d'un essai, fixé par l'adaptateur : il sert
    à ne lancer un nouvel essai que s'il peut se terminer dans le budget.
    """
    attempt_timeout_s: float
    delays_s: tuple[float, ...] = (1.0, 2.0)
    budget_s: float = 60.0

    def next_delay(self, attempt: int, elapsed_s: float) -> float | None:
        """Attente avant l'essai `attempt + 1`, ou None s'il ne doit pas avoir lieu."""
        if attempt > len(self.delays_s):
            return None
        delay = self.delays_s[attempt - 1]
        if elapsed_s + delay + self.attempt_timeout_s > self.budget_s:
            return None
        return delay
