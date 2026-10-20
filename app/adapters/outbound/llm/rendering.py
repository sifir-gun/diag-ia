"""Mise en forme des réponses pour le modèle. Les balises isolent les données."""
from __future__ import annotations

from app.application.ports import AdviceRequest
from app.domain.questions import QUESTIONS
from app.domain.scoring import PARTS


def build_user_content(request: AdviceRequest) -> str:
    lines = ["<reponses>"]
    for q in QUESTIONS:
        value = request.answers.get(q.key)
        if isinstance(value, list):
            value = ", ".join(value)
        lines.append(f"- {q.label} : {value}")
    lines += ["</reponses>", "",
              f"<score>{request.score.total}/100, niveau « {request.score.label} »</score>",
              "<detail_score>"]
    for key, label, maximum in PARTS:
        lines.append(f"- {label} : {request.score.breakdown.get(key, 0)}/{maximum}")
    lines.append("</detail_score>")
    return "\n".join(lines)
