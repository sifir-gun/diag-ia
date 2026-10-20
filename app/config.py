"""Configuration lue dans les variables d'environnement."""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from functools import lru_cache


class ConfigurationError(ValueError):
    """Configuration incohérente : l'application refuse de démarrer."""


LLM_BACKENDS = ("vertex", "fake")
STORE_BACKENDS = ("bigquery", "memory")
THINKING_LEVELS = ("minimal", "low", "medium", "high")


def _price(name: str, default: float) -> float:
    """Absente ou vide : valeur par défaut. Sinon un nombre fini, positif ou nul."""
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        value = float(raw)
    except ValueError:
        raise ConfigurationError(f"{name}={raw!r} : un nombre est attendu") from None
    if not math.isfinite(value) or value < 0:
        raise ConfigurationError(f"{name}={raw!r} : un nombre fini, positif ou nul, est attendu")
    return value


def _choice(name: str, default: str, allowed: tuple[str, ...]) -> str:
    value = os.getenv(name, default)
    if value not in allowed:
        raise ConfigurationError(f"{name}={value!r} : valeurs possibles {', '.join(allowed)}")
    return value


@dataclass(frozen=True)
class Settings:
    project: str
    vertex_location: str
    gemini_model: str
    thinking_level: str
    bq_dataset: str
    bq_table: str
    prompt_version: str
    price_input_usd_per_mtok: float
    price_output_usd_per_mtok: float
    llm_backend: str
    store_backend: str
    contact_email: str


@lru_cache
def get_settings() -> Settings:
    """Lit et valide la configuration : toute incohérence empêche le démarrage."""
    llm_backend = _choice("LLM_BACKEND", "vertex", LLM_BACKENDS)
    store_backend = _choice("STORE_BACKEND", "bigquery", STORE_BACKENDS)
    project = (os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "").strip()
    if not project and (llm_backend == "vertex" or store_backend == "bigquery"):
        raise ConfigurationError(
            f"GCP_PROJECT (ou GOOGLE_CLOUD_PROJECT) vide alors que LLM_BACKEND={llm_backend} et STORE_BACKEND={store_backend} : "
            "les adaptateurs réels ont besoin du projet")
    return Settings(
        project=project,
        vertex_location=os.getenv("VERTEX_LOCATION", "global"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        thinking_level=_choice("THINKING_LEVEL", "minimal", THINKING_LEVELS),
        bq_dataset=os.getenv("BQ_DATASET", "diagnostic"),
        bq_table=os.getenv("BQ_TABLE", "diagnostics"),
        prompt_version=os.getenv("PROMPT_VERSION", "v2"),
        price_input_usd_per_mtok=_price("PRICE_INPUT_USD_PER_MTOK", 1.50),
        price_output_usd_per_mtok=_price("PRICE_OUTPUT_USD_PER_MTOK", 9.00),
        llm_backend=llm_backend,
        store_backend=store_backend,
        contact_email=os.getenv("CONTACT_EMAIL", ""),
    )
