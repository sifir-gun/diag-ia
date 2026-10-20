import pytest

from app.adapters.outbound.prompts import FilePromptProvider
from app.bootstrap import PROMPTS_DIR
from app.config import get_settings

# Empreintes enregistrées dans BigQuery avec chaque diagnostic : une version
# publiée ne change jamais, sinon ses diagnostics deviennent invérifiables.
PUBLISHED = {
    "v1": "1639f38c4004a4210ee19bcba8bc11a218b3195ffc5729aa65e7725624589751",
    "v2": "e06e950dc371929b3806e4709353cf93d564c703fe881ff429c7c7df2f49b7dc",
}


@pytest.fixture
def default_settings(monkeypatch):
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()


def test_default_prompt_version_loads(default_settings):
    prompt = FilePromptProvider(PROMPTS_DIR).load(default_settings.prompt_version)
    assert prompt.version == default_settings.prompt_version
    assert prompt.text.strip()


@pytest.mark.parametrize("version, sha256", PUBLISHED.items())
def test_published_prompts_are_frozen(version, sha256):
    assert FilePromptProvider(PROMPTS_DIR).load(version).sha256 == sha256
