---
name: review-points-recurrents
description: Points à vérifier à chaque relecture diag-ia (prompts, adaptateur Gemini, normalisation du conseil, configuration stricte), constatés lors des relectures
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
- `_decode_entity` (gemini.py) applique `_printable` aux entités nommées comme aux codes : « &Tab; » et « &ZeroWidthSpace; » restent intacts et le domaine rejette ; garder ces deux tests. Guney a clos les raffinements sur les entités : toute remarque mineure à ce sujet va en une ligne dans la section Bonus du PLAN, seul un manquement à AGENTS.md, à l’échec fermé ou à la règle de dépendance est bloquant.
- Un adaptateur de sortie peut importer `app.domain` (ex. `HTML_ENTITY` dans gemini.py) : conforme à `tests/test_architecture.py`.
- Les commentaires de code utilisent l’apostrophe droite ; la règle ’ ne vaut que pour les textes visibles par l’utilisateur.
- Configuration (phase 5) : `get_settings()` valide backends, projet et `PRICE_*` (`ConfigurationError`) ; les `else` de `bootstrap.py` comptent sur cette validation, un `Settings(...)` construit à la main la contourne.
- Toute fixture qui appelle `get_settings()` doit fixer `LLM_BACKEND=fake` et `STORE_BACKEND=memory` (ou un projet), sinon la config par défaut est refusée ; vider le cache lru avant et après.
- Cloud Run reçoit `GCP_PROJECT` par `--set-env-vars` de `cloudbuild.yaml` : toute nouvelle variable obligatoire doit y figurer, sinon la révision ne démarre plus.
- Champ `model` des diagnostics = `<GEMINI_MODEL>/<THINKING_LEVEL>` depuis le 2026-10-21 (couvert par l’empreinte) ; les anciens gardent `gemini-3.5-flash` sans suffixe et doivent rester vérifiables.
- google-genai 2.31 accepte un `thinking_level` inconnu avec un simple `UserWarning` : `_choice("THINKING_LEVEL", ...)` de `app/config.py` est le seul garde-fou, ne pas l’affaiblir.
- `GeminiAdviceGenerator` accepte un `client` injectable ; les tests qui l’instancient importent quand même `google.genai.types` (présent dans requirements.txt, donc toléré).
- Nouvel essai (2026-10-21) : budget de 60 s dans `app/application/retry.py`, délai de 20 s par appel dans l’adaptateur Gemini (`TIMEOUT_S`, lu par bootstrap) ; ne pas déplacer l’un dans l’autre.
- google-genai 2.31 : sans `retry_options`, le SDK ne réessaie jamais (`stop_after_attempt(1)`) ; le seul nouvel essai est celui du cas d’usage.
- `HttpOptions.timeout` devient un `httpx.Timeout` par phase (connexion, lecture, écriture), pas un plafond total : le budget de 60 s reste nominal, à quelques secondes près.
- Avec un certificat client mTLS, le SDK passe par `requests` (AuthorizedSession) : son délai dépassé ne serait pas un `httpx.TimeoutException`, donc pas réessayé.
- Les `APIError` non passagères (400, 500) sortent de l’adaptateur (toléré, attrapé en `advice_failed` avec le seul nom du type) ; à signaler sans bloquer.
- `latency_ms` (BigQuery et `diagnostic_completed`) inclut les nouveaux essais et attentes ; `attempts` n’existe que dans l’événement.
- Cocher la tâche de `PLAN.md` fait partie du commit (CLAUDE.md) : le signaler si la case reste vide.
- Ce dossier de mémoire est versionné dans un dépôt public : ni secret ni donnée personnelle, et pas de tiret cadratin (règle de style du projet).

**Why:** constats faits pendant les relectures de la consigne v2 et du décodage des entités HTML renvoyées par Gemini.
**How to apply:** passer ces points en revue dès qu’un diff touche `prompts/`, `app/adapters/outbound/llm/`, `app/domain/advice.py`, `app/config.py`, `cloudbuild.yaml` ou ce dossier.
