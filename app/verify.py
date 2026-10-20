"""Point d'entrée de vérification : python -m app.verify <reference>"""
import sys

from app.adapters.inbound.cli.verify import run
from app.bootstrap import build_container
from app.config import get_settings

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(64)
    sys.exit(run(build_container(get_settings()).verify_diagnostic, sys.argv[1]))
