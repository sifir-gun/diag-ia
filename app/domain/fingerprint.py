"""Empreintes SHA-256 : chaque diagnostic peut être vérifié après coup."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Mapping

from app.domain.model import Advice, Diagnostic, Fingerprints, PromptRef, Score


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_text(canonical_json(obj))


def shown_document(score: Score, advice: Advice) -> dict[str, Any]:
    """Exactement ce qui est montré à l'utilisateur."""
    return {
        "score": score.total,
        "score_breakdown": dict(score.breakdown),
        "maturity_label": score.label,
        "summary": advice.summary,
        "recommendations": [asdict(r) for r in advice.recommendations],
    }


def compute_fingerprints(*, diagnostic_id: str, created_at: datetime,
                         answers: Mapping[str, object], score: Score, advice: Advice,
                         prompt: PromptRef, model: str) -> Fingerprints:
    input_sha = sha256_json(dict(answers))
    output_sha = sha256_json(shown_document(score, advice))
    record_sha = sha256_json({
        "diagnostic_id": diagnostic_id,
        "created_at": created_at.isoformat(),
        "input_sha256": input_sha,
        "output_sha256": output_sha,
        "prompt_sha256": prompt.sha256,
        "model": model,
    })
    return Fingerprints(input_sha256=input_sha, output_sha256=output_sha, record_sha256=record_sha)


def verify(diagnostic: Diagnostic) -> bool:
    """Recalcule les trois empreintes et les compare à celles enregistrées."""
    return compute_fingerprints(
        diagnostic_id=diagnostic.id, created_at=diagnostic.created_at,
        answers=diagnostic.answers, score=diagnostic.score, advice=diagnostic.advice,
        prompt=diagnostic.prompt, model=diagnostic.model,
    ) == diagnostic.fingerprints
