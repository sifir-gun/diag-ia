import json
from types import SimpleNamespace

import pytest

from app.adapters.outbound.llm.gemini import GeminiAdviceGenerator, _AdviceSchema, _to_domain
from app.application.ports import AdviceRequest, AdviceTemporarilyUnavailable, Prompt
from app.domain.advice import InvalidAdvice, normalize_advice
from app.domain.scoring import compute_score
from tests.fakes import VALID_ANSWERS


def model_json(**overrides):
    rec = {"title": "Automatiser les relances", "rationale": "Justification",
           "estimated_gain": "2 h", "effort": "faible", "confidence": 0.8}
    rec.update(overrides)
    return json.dumps({"summary": "Niveau &laquo; En d&eacute;marrage &raquo;",
                       "recommendations": [rec]})


def test_html_entities_from_the_model_are_decoded():
    advice = _to_domain(_AdviceSchema.model_validate_json(
        model_json(rationale="Vos donn&eacute;es, l&#39;&eacute;quipe", estimated_gain="5 &agrave; 10 h")))
    assert advice.summary == "Niveau « En démarrage »"
    rec = advice.recommendations[0]
    assert rec.rationale == "Vos données, l'équipe"
    assert rec.estimated_gain == "5 à 10 h"


def test_only_entities_ending_with_a_semicolon_are_decoded():
    advice = _to_domain(_AdviceSchema.model_validate_json(
        model_json(rationale="Revoir les &parametres et la R&D", estimated_gain="2 &agrave; 5 h")))
    rec = advice.recommendations[0]
    assert rec.rationale == "Revoir les &parametres et la R&D"
    assert rec.estimated_gain == "2 à 5 h"


def rationale_after_adapter(rationale):
    return _to_domain(_AdviceSchema.model_validate_json(model_json(rationale=rationale)))


@pytest.mark.parametrize("entity, char", [
    ("&eacute;", "é"),       # entité nommée connue
    ("&#233;", "é"),         # référence décimale
    ("&#xE9;", "é"),         # référence hexadécimale
    ("&#160;", " "),    # espace insécable : une espace compte comme imprimable
    ("&#8239;", " "),   # espace fine insécable, typographie française
    ("&#0000233;", "é"),     # zéros de tête autorisés
])
def test_real_entities_are_decoded(entity, char):
    assert rationale_after_adapter(f"a{entity}b").recommendations[0].rationale == f"a{char}b"


@pytest.mark.parametrize("entity", [
    "&notit;",     # nom inconnu qui commence par l'entité historique « &not »
    "&eacutex;",   # nom inconnu qui commence par « &eacute »
    "&Tab;",       # entité nommée connue, mais tabulation non imprimable
    "&ZeroWidthSpace;",  # entité nommée connue, mais caractère invisible (Cf)
    "&#0;",        # caractère nul
    "&#146;",      # caractère de contrôle C1
    "&#xD800;",    # demi-code de substitution, pas un caractère
    "&#1114112;",  # au-delà de U+10FFFF
    "&#x110000;",  # au-delà de U+10FFFF, en hexadécimal
    "&#x10FFFF;",  # non-caractère
    "&#00;",       # caractère nul écrit avec des zéros de tête
    "&#" + "9" * 5000 + ";",  # au-delà de la limite de conversion d'int() en base 10
])
def test_unknown_or_invalid_entities_are_left_for_the_domain_to_reject(entity):
    advice = rationale_after_adapter(f"a{entity}b")
    assert advice.recommendations[0].rationale == f"a{entity}b"
    with pytest.raises(InvalidAdvice):
        normalize_advice(advice)


def test_effort_is_decoded_before_validation():
    advice = _to_domain(_AdviceSchema.model_validate_json(model_json(effort="&eacute;lev&eacute;")))
    assert advice.recommendations[0].effort == "élevé"


class StubModels:
    """Remplace client.models : enregistre l'appel et renvoie une réponse prête."""

    def __init__(self, text: str):
        self.calls = []
        self._text = text

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        usage = SimpleNamespace(prompt_token_count=1000, candidates_token_count=400,
                                thoughts_token_count=0)
        return SimpleNamespace(parsed=None, text=self._text, usage_metadata=usage)


def stub_generator(level="minimal"):
    models = StubModels(model_json())
    generator = GeminiAdviceGenerator("projet", "global", "gemini-3.5-flash", level,
                                      client=SimpleNamespace(models=models))
    return generator, models


def call(generator):
    return generator.generate(Prompt(version="v2", text="consigne", sha256="0" * 64),
                              AdviceRequest(answers=VALID_ANSWERS, score=compute_score(VALID_ANSWERS)))


@pytest.mark.parametrize("level", ["minimal", "high"])
def test_thinking_level_is_sent_to_the_model(level):
    generator, models = stub_generator(level)
    call(generator)
    assert models.calls[0]["config"].thinking_config.thinking_level.value == level.upper()


def test_model_label_carries_the_thinking_level():
    generator, _ = stub_generator("minimal")
    assert call(generator).model == "gemini-3.5-flash/minimal"


class FailingModels:
    def __init__(self, error: Exception):
        self._error = error

    def generate_content(self, **kwargs):
        raise self._error


def failing_generator(error):
    return GeminiAdviceGenerator("projet", "global", "gemini-3.5-flash", "minimal",
                                 client=SimpleNamespace(models=FailingModels(error)))


def api_error(code):
    from google.genai import errors
    return errors.APIError(code, {"error": {"code": code, "message": "indisponible", "status": "X"}})


def timeout_error():
    import httpx
    return httpx.ReadTimeout("délai dépassé")


@pytest.mark.parametrize("make_error, reason", [
    (lambda: api_error(503), "503"), (lambda: api_error(429), "429"), (timeout_error, "timeout"),
])
def test_overload_quota_and_timeout_are_temporary(make_error, reason):
    with pytest.raises(AdviceTemporarilyUnavailable) as caught:
        call(failing_generator(make_error()))
    assert caught.value.reason == reason


@pytest.mark.parametrize("code", [400, 500])
def test_other_api_errors_are_not_temporary(code):
    from google.genai import errors
    with pytest.raises(errors.APIError):
        call(failing_generator(api_error(code)))


def test_each_call_has_a_20_second_timeout():
    generator, models = stub_generator()
    call(generator)
    assert models.calls[0]["config"].http_options.timeout == 20_000
