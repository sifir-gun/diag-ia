"""Adaptateur Gemini, via Gemini Enterprise Agent Platform (anciennement Vertex AI).

Le schéma Pydantic ci-dessous est une couche anticorruption : il décrit le JSON
imposé au modèle, puis il est traduit en objets du domaine.
Authentification par le compte de service de Cloud Run : aucune clé API.
"""
from __future__ import annotations

import re
import unicodedata
from html.entities import html5
from typing import Literal

from pydantic import BaseModel, ValidationError, field_validator

from app.adapters.outbound.llm.rendering import build_user_content
from app.application.ports import (
    AdviceGenerationError, AdviceRequest, AdviceTemporarilyUnavailable, GeneratedAdvice, Prompt,
)
from app.domain.advice import HTML_ENTITY
from app.domain.model import Advice, Recommendation


def _printable(char: str) -> bool:
    # Les espaces (catégorie Zs) comptent comme imprimables : l'espace insécable
    # et l'espace fine insécable font partie de la typographie française.
    return char.isprintable() or unicodedata.category(char) == "Zs"


def _decode_entity(match: re.Match[str]) -> str:
    entity = match.group(0)
    if entity[1] != "#":
        # Nom exact uniquement : html.unescape décoderait « &notit; » en « ¬it; ».
        # Même contrôle que pour les codes : « &Tab; » reste intact comme « &#9; ».
        decoded = html5.get(entity[1:])
        if decoded is None or not all(_printable(char) for char in decoded):
            return entity
        return decoded
    hexa = entity[2] in "xX"
    digits = (entity[3:-1] if hexa else entity[2:-1]).lstrip("0") or "0"
    # U+10FFFF tient en 6 chiffres hexadécimaux ou 7 décimaux. Au-delà, on ne
    # convertit pas : int() refuse plus de 4300 chiffres en base 10.
    if len(digits) > (6 if hexa else 7):
        return entity
    code = int(digits, 16 if hexa else 10)
    if code > 0x10FFFF or 0xD800 <= code <= 0xDFFF or not _printable(chr(code)):
        return entity
    return chr(code)


def _decode_entities(value: object) -> object:
    # Le modèle renvoie parfois des entités HTML (&eacute;) : on les décode
    # avant validation, pour que « élevé » passe aussi le contrôle du Literal.
    # Seules les vraies entités sont décodées ; les autres restent intactes
    # et le filet du domaine (HTML_ENTITY) rejette alors le conseil.
    if not isinstance(value, str):
        return value
    return HTML_ENTITY.sub(_decode_entity, value)


class _RecommendationSchema(BaseModel):
    title: str
    rationale: str
    estimated_gain: str
    effort: Literal["faible", "moyen", "élevé"]
    confidence: float

    _decode = field_validator("title", "rationale", "estimated_gain", "effort",
                              mode="before")(_decode_entities)


class _AdviceSchema(BaseModel):
    summary: str
    recommendations: list[_RecommendationSchema]

    _decode = field_validator("summary", mode="before")(_decode_entities)


# Délai httpx d'un essai, par opération réseau (connexion, pool, envoi, lecture entre deux paquets)
# et non pour l'appel entier :
# détail de transport. Le budget total est une règle du cas d'usage.
TIMEOUT_S = 20
TEMPORARY_CODES = (429, 503)


class GeminiAdviceGenerator:
    def __init__(self, project: str, location: str, model: str, thinking_level: str,
                 client: object | None = None):
        import httpx
        from google.genai import errors, types

        self._types = types
        self._api_error = errors.APIError
        self._timeout_error = httpx.TimeoutException
        if client is None:
            from google import genai
            client = genai.Client(enterprise=True, project=project, location=location)
        self._client = client  # injectable pour les tests, sans réseau
        self._model = model
        self._thinking_level = thinking_level

    def generate(self, prompt: Prompt, request: AdviceRequest) -> GeneratedAdvice:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=build_user_content(request),
                config=self._types.GenerateContentConfig(
                    system_instruction=prompt.text,
                    response_mime_type="application/json",
                    response_schema=_AdviceSchema,
                    thinking_config=self._types.ThinkingConfig(thinking_level=self._thinking_level),
                    http_options=self._types.HttpOptions(timeout=TIMEOUT_S * 1000),  # millisecondes
                ),
            )
        except self._timeout_error as exc:
            raise AdviceTemporarilyUnavailable("timeout") from exc
        except self._api_error as exc:
            if exc.code in TEMPORARY_CODES:
                raise AdviceTemporarilyUnavailable(str(exc.code)) from exc
            raise
        parsed = getattr(response, "parsed", None)
        if not isinstance(parsed, _AdviceSchema):
            try:
                parsed = _AdviceSchema.model_validate_json(response.text or "")
            except ValidationError as exc:
                raise AdviceGenerationError("JSON du modèle invalide") from exc

        usage = response.usage_metadata
        input_tokens = (usage.prompt_token_count or 0) if usage else 0
        output_tokens = ((usage.candidates_token_count or 0)
                         + (getattr(usage, "thoughts_token_count", None) or 0)) if usage else 0
        # Le niveau de réflexion fait partie du modèle : il est stocké et couvert par l'empreinte.
        return GeneratedAdvice(advice=_to_domain(parsed), model=f"{self._model}/{self._thinking_level}",
                               input_tokens=input_tokens, output_tokens=output_tokens)


def _to_domain(schema: _AdviceSchema) -> Advice:
    return Advice(
        summary=schema.summary,
        recommendations=tuple(Recommendation(**rec.model_dump()) for rec in schema.recommendations),
    )
