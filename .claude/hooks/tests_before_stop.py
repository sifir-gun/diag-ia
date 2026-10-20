"""Hook Stop : relance les tests si du code a changé, et empêche de conclure s'ils échouent.

Code de sortie 2 : Claude ne peut pas s'arrêter et reçoit la sortie des tests.
Le drapeau stop_hook_active évite une boucle infinie : un seul essai de correction
par réponse, ensuite la main revient à l'humain.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
WATCHED = ["app", "tests", "prompts"]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    if payload.get("stop_hook_active"):
        return 0

    # Rien n'a changé dans le code : pas besoin de tester.
    status = subprocess.run(["git", "status", "--porcelain", "--", *WATCHED],
                            cwd=ROOT, capture_output=True, text=True)
    if status.returncode == 0 and not status.stdout.strip():
        return 0

    venv_python = ROOT / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable
    if subprocess.run([python, "-c", "import pytest"], cwd=ROOT, capture_output=True).returncode != 0:
        return 0  # environnement pas encore installé : on ne bloque pas

    result = subprocess.run([python, "-m", "pytest", "-q", "-x", "--no-header"],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        return 0
    tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-40:])
    print(f"Les tests échouent après tes modifications. Corrige avant de conclure.\n\n{tail}",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
