"""Adaptateurs des ports Clock et IdGenerator."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class UuidIdGenerator:
    def new_id(self) -> str:
        return uuid.uuid4().hex
