"""Point d'entrée web (uvicorn app.main:app)."""
from app.adapters.inbound.web.app import create_app
from app.bootstrap import build_container
from app.config import get_settings

settings = get_settings()
container = build_container(settings)
app = create_app(run_diagnostic=container.run_diagnostic, contact_email=settings.contact_email)
