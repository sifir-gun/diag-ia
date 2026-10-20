import json

from app.adapters.outbound.llm.gemini import _AdviceSchema, _to_domain


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


def test_effort_is_decoded_before_validation():
    advice = _to_domain(_AdviceSchema.model_validate_json(model_json(effort="&eacute;lev&eacute;")))
    assert advice.recommendations[0].effort == "élevé"
