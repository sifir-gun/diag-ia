import pytest
from fastapi.testclient import TestClient

from app.adapters.inbound.web.app import create_app
from tests.fakes import make_use_case


@pytest.fixture
def parts():
    return make_use_case()


@pytest.fixture
def client(parts):
    use_case, _, _, _ = parts
    with TestClient(create_app(run_diagnostic=use_case, contact_email="contact@example.com")) as c:
        yield c
