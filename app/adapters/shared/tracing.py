"""Identifiant de trace Cloud, partagé entre l'entrée web et les logs."""
from __future__ import annotations

from contextvars import ContextVar

trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)


def parse_trace_header(header: str | None) -> str | None:
    """X-Cloud-Trace-Context : TRACE_ID/SPAN_ID;o=1"""
    if not header:
        return None
    return header.split("/", 1)[0] or None
