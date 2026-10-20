from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.domain.advice import InvalidAdvice, normalize_advice
from app.domain.fingerprint import compute_fingerprints, sha256_json, verify
from app.domain.model import Advice, Diagnostic, PromptRef, Recommendation, Usage
from app.domain.questions import QUESTIONS_BY_KEY
from app.domain.scoring import WEIGHTS, compute_score, maturity_label
from app.domain.submission import InvalidSubmission, validate_submission
from tests.fakes import VALID_ANSWERS


def rec(confidence=0.5, effort="moyen"):
    return Recommendation("Titre", "Justification", "2 h par semaine", effort, confidence)


def test_every_scored_option_has_a_weight():
    for key, weights in WEIGHTS.items():
        assert set(weights) == set(QUESTIONS_BY_KEY[key].options)


def test_score_is_deterministic_and_explained():
    score = compute_score(VALID_ANSWERS)
    assert score.total == 20 + 10 + 10 + 8
    assert score.label == "En démarrage"
    assert sum(score.breakdown.values()) == score.total
    assert maturity_label(0) == "Débutant" and maturity_label(100) == "Avancé"


def test_submission_collects_every_error():
    with pytest.raises(InvalidSubmission) as exc:
        validate_submission({"secteur": "BTP"}, consent=False, contact_email="pas-un-mail")
    errors = exc.value.errors
    assert "effectif" in errors and "consent" in errors and "contact_email" in errors
    assert "secteur" not in errors


def test_normalize_bounds_and_truncates():
    advice = Advice(" Synthèse ", (rec(1.4), rec(-0.2), rec(), rec(), rec()))
    clean = normalize_advice(advice)
    assert len(clean.recommendations) == 3
    assert [r.confidence for r in clean.recommendations[:2]] == [1.0, 0.0]
    assert clean.summary == "Synthèse"


@pytest.mark.parametrize("advice", [
    Advice("Synthèse", ()),
    Advice("", (rec(),)),
    Advice("Synthèse", (rec(effort="énorme"),)),
])
def test_normalize_rejects_broken_advice(advice):
    with pytest.raises(InvalidAdvice):
        normalize_advice(advice)


@pytest.mark.parametrize("advice", [
    Advice("Niveau &laquo; En d&eacute;marrage &raquo;", (rec(),)),
    Advice("Synthèse", (Recommendation("R&amp;D", "Justification", "2 h", "moyen", 0.5),)),
    Advice("Synthèse", (Recommendation("Titre", "L&#39;équipe", "2 h", "moyen", 0.5),)),
    Advice("Synthèse", (Recommendation("Titre", "Justification", "2 &agrave; 5 h", "moyen", 0.5),)),
])
def test_normalize_rejects_html_entities_left_by_the_adapter(advice):
    with pytest.raises(InvalidAdvice):
        normalize_advice(advice)


def test_normalize_keeps_a_bare_ampersand():
    advice = Advice("R&D et PME", (Recommendation("Lancer la R&D", "Justification", "2 h", "moyen", 0.5),))
    assert normalize_advice(advice).recommendations[0].title == "Lancer la R&D"


def test_normalize_uses_typographic_apostrophes():
    advice = Advice("L'IA aide l'équipe",
                    (Recommendation("Former l'équipe", "Aujourd'hui", "Jusqu'à 5 h", "moyen", 0.5),))
    clean = normalize_advice(advice)
    assert clean.summary == "L’IA aide l’équipe"
    rec_out = clean.recommendations[0]
    assert (rec_out.title, rec_out.rationale, rec_out.estimated_gain) == (
        "Former l’équipe", "Aujourd’hui", "Jusqu’à 5 h")


def test_hash_ignores_key_order():
    assert sha256_json({"a": 1, "b": 2}) == sha256_json({"b": 2, "a": 1})


def test_any_change_breaks_the_fingerprint():
    score = compute_score(VALID_ANSWERS)
    advice = Advice("Synthèse", (rec(),))
    created = datetime(2026, 10, 20, tzinfo=timezone.utc)
    prompt = PromptRef("v1", "abc")
    prints = compute_fingerprints(diagnostic_id="d1", created_at=created, answers=VALID_ANSWERS,
                                  score=score, advice=advice, prompt=prompt, model="m")
    d = Diagnostic("d1", created, VALID_ANSWERS, score, advice, prompt, "m",
                   Usage(1, 1, 1, 0.0), prints)
    assert verify(d)
    assert not verify(replace(d, model="autre-modele"))
    assert not verify(replace(d, score=replace(score, total=99)))
    assert not verify(replace(d, answers={**VALID_ANSWERS, "budget": "Plus de 50 000 €"}))
