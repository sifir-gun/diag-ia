"""La règle de dépendance de l'hexagone, vérifiée à chaque build.

domaine <- application <- adaptateurs <- racine de composition
"""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent.parent / "app"
FRAMEWORKS = ("fastapi", "starlette", "pydantic", "google", "jinja2", "uvicorn")

RULES = {
    "domain": ("app.application", "app.adapters", "app.bootstrap", "app.config", *FRAMEWORKS),
    "application": ("app.adapters", "app.bootstrap", "app.config", *FRAMEWORKS),
    "adapters/inbound": ("app.adapters.outbound", "app.bootstrap", "google"),
    "adapters/outbound": ("app.adapters.inbound", "app.bootstrap", "fastapi", "starlette"),
}


def imports_of(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


CASES = [(layer, f) for layer in RULES for f in sorted((APP / layer).rglob("*.py"))]


@pytest.mark.parametrize("layer, path", CASES, ids=[str(p.relative_to(APP)) for _, p in CASES])
def test_dependency_rule(layer, path):
    forbidden = RULES[layer]
    bad = sorted(name for name in imports_of(path)
                 if any(name == f or name.startswith(f + ".") for f in forbidden))
    assert not bad, f"{path.relative_to(APP)} importe {bad}, interdit pour la couche {layer}"
