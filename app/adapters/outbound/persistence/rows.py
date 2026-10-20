"""Traduction entre l'entité Diagnostic et une ligne de la table BigQuery."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Mapping

from app.domain.fingerprint import canonical_json
from app.domain.model import (
    Advice, Diagnostic, Fingerprints, PromptRef, Recommendation, Score, Usage,
)


def to_row(d: Diagnostic) -> dict[str, Any]:
    return {
        "diagnostic_id": d.id,
        "created_at": d.created_at.isoformat(),
        "answers": canonical_json(dict(d.answers)),
        "score": d.score.total,
        "score_breakdown": canonical_json(dict(d.score.breakdown)),
        "maturity_label": d.score.label,
        "summary": d.advice.summary,
        "recommendations": canonical_json([asdict(r) for r in d.advice.recommendations]),
        "prompt_version": d.prompt.version,
        "prompt_sha256": d.prompt.sha256,
        "model": d.model,
        "input_tokens": d.usage.input_tokens,
        "output_tokens": d.usage.output_tokens,
        "latency_ms": d.usage.latency_ms,
        "cost_usd": d.usage.cost_usd,
        "input_sha256": d.fingerprints.input_sha256,
        "output_sha256": d.fingerprints.output_sha256,
        "record_sha256": d.fingerprints.record_sha256,
        "contact_email": d.contact_email,
    }


def from_row(row: Mapping[str, Any]) -> Diagnostic:
    created = row["created_at"]
    if isinstance(created, str):
        created = datetime.fromisoformat(created)
    recommendations = tuple(Recommendation(**r) for r in _obj(row["recommendations"]))
    return Diagnostic(
        id=row["diagnostic_id"],
        created_at=created,
        answers=_obj(row["answers"]),
        score=Score(total=row["score"], breakdown=_obj(row["score_breakdown"]),
                    label=row["maturity_label"]),
        advice=Advice(summary=row["summary"], recommendations=recommendations),
        prompt=PromptRef(version=row["prompt_version"], sha256=row["prompt_sha256"]),
        model=row["model"],
        usage=Usage(input_tokens=row["input_tokens"], output_tokens=row["output_tokens"],
                    latency_ms=row["latency_ms"], cost_usd=row["cost_usd"]),
        fingerprints=Fingerprints(input_sha256=row["input_sha256"],
                                  output_sha256=row["output_sha256"],
                                  record_sha256=row["record_sha256"]),
        contact_email=row.get("contact_email"),
    )


def _obj(value: Any) -> Any:
    """BigQuery peut renvoyer une colonne JSON déjà décodée ou sous forme de texte."""
    return json.loads(value) if isinstance(value, str) else value
