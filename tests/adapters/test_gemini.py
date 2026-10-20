import json

import pytest

from app.adapters.outbound.llm.gemini import _AdviceSchema, _to_domain
from app.domain.advice import InvalidAdvice, normalize_advice


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
