import pytest

from app.config import ConfigurationError, get_settings

VARIABLES = (
    "GCP_PROJECT", "GOOGLE_CLOUD_PROJECT", "LLM_BACKEND", "STORE_BACKEND",
    "PRICE_INPUT_USD_PER_MTOK", "PRICE_OUTPUT_USD_PER_MTOK",
)


@pytest.fixture
def env(monkeypatch):
    """Environnement local valide, sans projet, cache vidé avant et après."""
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LLM_BACKEND", "fake")
    monkeypatch.setenv("STORE_BACKEND", "memory")
    get_settings.cache_clear()
    yield monkeypatch
    get_settings.cache_clear()


def test_local_adapters_start_without_project(env):
    settings = get_settings()
    assert (settings.project, settings.llm_backend, settings.store_backend) == ("", "fake", "memory")


def test_real_adapters_start_with_project(env):
    env.setenv("LLM_BACKEND", "vertex")
    env.setenv("STORE_BACKEND", "bigquery")
    env.setenv("GCP_PROJECT", "wengraf-diag-ia")
    assert get_settings().project == "wengraf-diag-ia"


def test_project_falls_back_to_google_cloud_project(env):
    env.setenv("STORE_BACKEND", "bigquery")
    env.setenv("GOOGLE_CLOUD_PROJECT", "wengraf-diag-ia")
    assert get_settings().project == "wengraf-diag-ia"


@pytest.mark.parametrize("variable, value", [("LLM_BACKEND", "fak"), ("STORE_BACKEND", "bq")])
def test_unknown_backend_is_refused(env, variable, value):
    env.setenv(variable, value)
    with pytest.raises(ConfigurationError, match=f"{variable}.*{value}"):
        get_settings()


@pytest.mark.parametrize("variable, value", [("LLM_BACKEND", "vertex"), ("STORE_BACKEND", "bigquery")])
@pytest.mark.parametrize("project", ["", "   "])
def test_real_adapter_without_project_is_refused(env, variable, value, project):
    env.setenv(variable, value)
    env.setenv("GCP_PROJECT", project)
    with pytest.raises(ConfigurationError, match="GCP_PROJECT"):
        get_settings()


@pytest.mark.parametrize("variable", ["PRICE_INPUT_USD_PER_MTOK", "PRICE_OUTPUT_USD_PER_MTOK"])
@pytest.mark.parametrize("value", ["abc", "-1", "nan", "inf"])
def test_invalid_price_is_refused(env, variable, value):
    env.setenv(variable, value)
    with pytest.raises(ConfigurationError, match=f"{variable}.*{value}"):
        get_settings()


def test_empty_price_keeps_default(env):
    env.setenv("PRICE_INPUT_USD_PER_MTOK", "")
    env.setenv("PRICE_OUTPUT_USD_PER_MTOK", "")
    settings = get_settings()
    assert (settings.price_input_usd_per_mtok, settings.price_output_usd_per_mtok) == (1.50, 9.00)


def test_valid_price_is_read(env):
    env.setenv("PRICE_INPUT_USD_PER_MTOK", "0.5")
    assert get_settings().price_input_usd_per_mtok == 0.5
