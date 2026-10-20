"""Adaptateur Gemini, via Gemini Enterprise Agent Platform (anciennement Vertex AI).

Le schéma Pydantic ci-dessous est une couche anticorruption : il décrit le JSON
imposé au modèle, puis il est traduit en objets du domaine.
Authentification par le compte de service de Cloud Run : aucune clé API.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ValidationError

from app.adapters.outbound.llm.rendering import build_user_content
from app.application.ports import AdviceGenerationError, AdviceRequest, GeneratedAdvice, Prompt
from app.domain.model import Advice, Recommendation


class _RecommendationSchema(BaseModel):
    title: str
    rationale: str
    estimated_gain: str
    effort: Literal["faible", "moyen", "élevé"]
    confidence: float


class _AdviceSchema(BaseModel):
    summary: str
    recommendations: list[_RecommendationSchema]


class GeminiAdviceGenerator:
    def __init__(self, project: str, location: str, model: str):
        from google import genai
        from google.genai import types

        self._types = types
        self._client = genai.Client(enterprise=True, project=project, location=location)
        self._model = model

    def generate(self, prompt: Prompt, request: AdviceRequest) -> GeneratedAdvice:
        response = self._client.models.generate_content(
            model=self._model,
            contents=build_user_content(request),
            config=self._types.GenerateContentConfig(
                system_instruction=prompt.text,
                response_mime_type="application/json",
                response_schema=_AdviceSchema,
            ),
        )
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
        return GeneratedAdvice(advice=_to_domain(parsed), model=self._model,
                               input_tokens=input_tokens, output_tokens=output_tokens)


def _to_domain(schema: _AdviceSchema) -> Advice:
    return Advice(
        summary=schema.summary,
        recommendations=tuple(Recommendation(**rec.model_dump()) for rec in schema.recommendations),
    )
