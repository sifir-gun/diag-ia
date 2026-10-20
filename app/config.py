"""Configuration lue dans les variables d'environnement."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    project: str
    vertex_location: str
    gemini_model: str
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
    return Settings(
        project=os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        vertex_location=os.getenv("VERTEX_LOCATION", "global"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        bq_dataset=os.getenv("BQ_DATASET", "diagnostic"),
        bq_table=os.getenv("BQ_TABLE", "diagnostics"),
        prompt_version=os.getenv("PROMPT_VERSION", "v1"),
        price_input_usd_per_mtok=_float("PRICE_INPUT_USD_PER_MTOK", 1.50),
        price_output_usd_per_mtok=_float("PRICE_OUTPUT_USD_PER_MTOK", 9.00),
        llm_backend=os.getenv("LLM_BACKEND", "vertex"),
        store_backend=os.getenv("STORE_BACKEND", "bigquery"),
        contact_email=os.getenv("CONTACT_EMAIL", ""),
    )
