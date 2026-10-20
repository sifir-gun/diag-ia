"""Adaptateur du port PromptProvider : des fichiers versionnés dans le repo."""
from __future__ import annotations

import re
from pathlib import Path

from app.application.ports import Prompt
from app.domain.fingerprint import sha256_text


class FilePromptProvider:
    def __init__(self, directory: Path):
        self._directory = directory
        self._cache: dict[str, Prompt] = {}

    def load(self, version: str) -> Prompt:
        if version not in self._cache:
            if not re.fullmatch(r"v\d+", version):
                raise ValueError(f"Version de prompt invalide : {version}")
            text = (self._directory / f"diagnostic_{version}.md").read_text(encoding="utf-8")
            self._cache[version] = Prompt(version=version, text=text, sha256=sha256_text(text))
        return self._cache[version]
