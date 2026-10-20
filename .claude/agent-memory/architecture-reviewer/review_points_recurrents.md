---
name: review-points-recurrents
description: Points à vérifier à chaque relecture diag-ia (prompts, adaptateur Gemini, normalisation du conseil), constatés lors des relectures
metadata:
  type: project
---

- Immutabilité des prompts : `test_published_prompts_are_frozen` (tests/adapters/test_prompts.py) fige les sha256 dans `PUBLISHED` ; à chaque nouvelle version publiée, vérifier qu’elle y est ajoutée avec l’entrée `Edit(prompts/diagnostic_vN.md)` de `permissions.deny` (étape 8 du skill `nouvelle-version-prompt`).
- Version par défaut : `test_default_prompt_version_loads` la charge (cache lru de `get_settings` vidé avant et après) ; `tests/fakes.py` reste en `v1`.
- Changement de version de prompt : vérifier `app/config.py`, `.env.example` et `cloudbuild.yaml` (skill `nouvelle-version-prompt`, étape 4).
- Pydantic 2.14 : un `field_validator(...)(fn)` assigné à un nom `_decode` est bien enregistré comme validateur (pas comme attribut privé) ; le SDK google-genai 2.31 passe par `model_validate_json`, donc par ces validateurs.
- Pydantic transforme un `ValueError` levé dans un validateur en `ValidationError` ; le SDK google-genai 2.31 avale ce `ValidationError` (`parsed` reste à None) et le repli de `generate` le convertit en `AdviceGenerationError` : échec fermé.
- `html.unescape` décode par préfixe d’entité historique (« &notit; » donne « ¬it; ») et change « &#0; » en U+FFFD : ne jamais le réintroduire dans l’adaptateur Gemini, qui décode via `html.entities.html5` (nom exact) et `chr` (code imprimable).
- Python 3.12 : `int()` en base 10 lève `ValueError` au-delà de 4300 chiffres (pas en base 16). Traité dans `_decode_entity` (gemini.py) : zéros de tête retirés, plus de 6 chiffres hexa ou 7 décimaux laissés intacts ; garder cette borne et son test (« &#9…9; » de 5000 chiffres) à toute retouche.
- Entités nommées HTML5 non filtrées par `_printable` : « &Tab; », « &NewLine; », « &ZeroWidthSpace; » sont décodées alors que « &#9; » ou « &#8203; » sont refusés (signalé en relecture, à trancher par Guney).
- Un adaptateur de sortie peut importer `app.domain` (ex. `HTML_ENTITY` dans gemini.py) : conforme à `tests/test_architecture.py`.
- Les commentaires de code utilisent l’apostrophe droite ; la règle ’ ne vaut que pour les textes visibles par l’utilisateur.
- Ce dossier de mémoire est versionné dans un dépôt public : ni secret ni donnée personnelle, et pas de tiret cadratin (règle de style du projet).

**Why:** constats faits pendant les relectures de la consigne v2 et du décodage des entités HTML renvoyées par Gemini.
**How to apply:** passer ces points en revue dès qu’un diff touche `prompts/`, `app/adapters/outbound/llm/`, `app/domain/advice.py` ou ce dossier.
