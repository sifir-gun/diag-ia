from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pricing:
    """Prix catalogue du modèle, en USD par million de tokens."""
    input_usd_per_mtok: float
    output_usd_per_mtok: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return round(input_tokens / 1e6 * self.input_usd_per_mtok
                     + output_tokens / 1e6 * self.output_usd_per_mtok, 6)
