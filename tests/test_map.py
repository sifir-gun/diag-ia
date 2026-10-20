"""MAP.md ne doit jamais mentir : chaque module y figure, chaque chemin cité existe."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = (ROOT / "MAP.md").read_text(encoding="utf-8")
CITED = set(re.findall(r"`([\w./-]+\.(?:py|md|json|sql|yaml|html|css))`", MAP))


def test_every_module_is_on_the_map():
    modules = {p.relative_to(ROOT).as_posix()
               for p in (ROOT / "app").rglob("*.py") if p.name != "__init__.py"}
    missing = sorted(modules - CITED)
    assert not missing, f"Modules absents de MAP.md : {missing}"


def test_map_only_points_to_existing_files():
    ghosts = sorted(p for p in CITED if not (ROOT / p).exists())
    assert not ghosts, f"MAP.md cite des fichiers qui n’existent pas : {ghosts}"
