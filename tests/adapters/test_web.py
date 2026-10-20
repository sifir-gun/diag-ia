from app.domain.questions import QUESTIONS
from tests.fakes import VALID_ANSWERS


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_form_lists_all_questions(client):
    html = client.get("/").text
    for q in QUESTIONS:
        assert f'id="q-{q.key}"' in html


def test_api_returns_a_traced_diagnostic(client, parts):
    res = client.post("/api/diagnostic", json={"answers": VALID_ANSWERS, "consent": True})
    assert res.status_code == 200
    body = res.json()
    assert body["score"] == 48 and len(body["recommendations"]) == 3
    assert len(body["record_sha256"]) == 64
    assert body["diagnostic_id"] in parts[2].rows


def test_api_maps_invalid_submission_to_422(client):
    answers = {**VALID_ANSWERS, "secteur": "Astronautique"}
    res = client.post("/api/diagnostic", json={"answers": answers, "consent": True})
    assert res.status_code == 422
    assert "secteur" in res.json()["detail"]


def test_form_flow_shows_result_and_contact(client, parts):
    res = client.post("/diagnostic", data={**VALID_ANSWERS, "consent": "on"})
    assert res.status_code == 200
    assert "Votre diagnostic" in res.text
    assert next(iter(parts[2].rows)) in res.text
    assert "mailto:contact@example.com" in res.text


def test_form_errors_keep_previous_answers(client):
    res = client.post("/diagnostic", data={"secteur": "BTP"})
    assert res.status_code == 422
    assert "Choisissez une réponse." in res.text
    assert 'value="BTP" checked' in res.text
