# Carte du projet

Deux usages : savoir quels fichiers toucher pour un changement donné, et savoir à quoi sert chaque fichier. `tests/test_map.py` vérifie que chaque module de `app/` figure ici et que chaque chemin cité existe : si la carte n’est plus à jour, le build échoue.

## Où modifier quoi

| Je veux… | Fichiers à toucher | Test qui protège |
|---|---|---|
| Changer une question ou ses options | `app/domain/questions.py`, puis les poids dans `app/domain/scoring.py` si la question est notée, et `tests/fakes.py` | `test_every_scored_option_has_a_weight` |
| Changer la grille de score ou les niveaux | `app/domain/scoring.py` | `test_score_is_deterministic_and_explained` |
| Changer la consigne du modèle | Une nouvelle version dans le dossier prompts, avec le skill `nouvelle-version-prompt` | `test_diagnostic_is_recorded_then_returned`, `test_published_prompts_are_frozen`, `test_default_prompt_version_loads` |
| Changer le format des recommandations | `app/domain/model.py`, `app/domain/advice.py`, `app/adapters/outbound/llm/gemini.py`, `app/adapters/outbound/llm/fake.py`, `app/adapters/inbound/web/schemas.py`, `app/adapters/inbound/web/templates/result.html`, `app/adapters/outbound/persistence/rows.py` | `test_normalize_bounds_and_truncates`, `test_row_round_trip_as_bigquery_returns_it` |
| Ajouter une colonne BigQuery | `app/adapters/outbound/persistence/rows.py`, `sql/schema_diagnostics.json`, `sql/audit.sql` | `test_row_round_trip_as_bigquery_returns_it` |
| Changer le design | `app/adapters/inbound/web/static/style.css` et les gabarits de `app/adapters/inbound/web/templates/` | `test_form_lists_all_questions` |
| Changer un message d’erreur affiché | `app/domain/submission.py`, `app/domain/questions.py` ou `app/adapters/inbound/web/html.py` | `test_form_errors_keep_previous_answers` |
| Ajouter un événement de log | `app/application/run_diagnostic.py`, puis la requête 3 de `sql/audit.sql` | `test_model_failure_records_nothing` |
| Ajouter une variable de configuration | `app/config.py`, `.env.example`, `cloudbuild.yaml`, et `app/bootstrap.py` si elle choisit un adaptateur | `tests/test_config.py` si elle doit être validée |
| Brancher un service externe | Skill `nouveau-port` | `test_dependency_rule` |
| Changer le déploiement | `cloudbuild.yaml`, `Dockerfile` | le build Cloud Build |

## Fichiers

### Domaine (`app/domain/`)

- `app/domain/model.py` : entités et objets-valeurs (Diagnostic, Score, Advice, Recommendation, Usage, Fingerprints).
- `app/domain/questions.py` : les 10 questions et la validation des réponses.
- `app/domain/submission.py` : soumission recevable (réponses, accord, e-mail).
- `app/domain/scoring.py` : grille de score fixe et niveaux de maturité.
- `app/domain/advice.py` : contrôle et normalisation du conseil produit par le modèle.
- `app/domain/fingerprint.py` : empreintes SHA-256 et vérification d’intégrité.

### Application (`app/application/`)

- `app/application/ports.py` : les six ports (AdviceGenerator, DiagnosticRepository, PromptProvider, EventPublisher, Clock, IdGenerator).
- `app/application/run_diagnostic.py` : cas d’usage principal, produire un diagnostic tracé.
- `app/application/verify_diagnostic.py` : cas d’usage d’audit, vérifier un diagnostic stocké.
- `app/application/pricing.py` : estimation du coût à partir des tokens.
- `app/application/errors.py` : erreurs d’application (conseil indisponible, enregistrement impossible).

### Adaptateurs d’entrée (`app/adapters/inbound/`)

- `app/adapters/inbound/web/app.py` : fabrique FastAPI, trace Cloud, route de santé.
- `app/adapters/inbound/web/html.py` : formulaire et page de résultat.
- `app/adapters/inbound/web/api.py` : API JSON.
- `app/adapters/inbound/web/schemas.py` : contrats HTTP, traduits depuis le domaine.
- `app/adapters/inbound/cli/verify.py` : vérification d’intégrité en ligne de commande.

### Adaptateurs de sortie (`app/adapters/outbound/`)

- `app/adapters/outbound/llm/gemini.py` : Gemini sur Agent Platform, schéma JSON imposé, couche anticorruption.
- `app/adapters/outbound/llm/fake.py` : faux modèle pour le local et les tests.
- `app/adapters/outbound/llm/rendering.py` : mise en forme des réponses envoyées au modèle.
- `app/adapters/outbound/persistence/bigquery.py` : stockage BigQuery.
- `app/adapters/outbound/persistence/memory.py` : stockage en mémoire.
- `app/adapters/outbound/persistence/rows.py` : traduction entre Diagnostic et ligne de table.
- `app/adapters/outbound/prompts.py` : chargement des prompts versionnés.
- `app/adapters/outbound/observability.py` : logs JSON pour Cloud Logging.
- `app/adapters/outbound/system.py` : horloge UTC et identifiants.
- `app/adapters/shared/tracing.py` : identifiant de trace partagé entre le web et les logs.

### Composition et points d’entrée

- `app/config.py` : configuration lue dans les variables d’environnement et validée : backend inconnu, projet vide avec un adaptateur réel ou prix invalide lèvent `ConfigurationError`.
- `app/bootstrap.py` : racine de composition, seul endroit qui choisit les adaptateurs.
- `app/main.py` : point d’entrée web pour uvicorn.
- `app/verify.py` : point d’entrée de vérification.

### Hors de `app/`

- `prompts/diagnostic_v1.md` : consigne du modèle, version 1, figée.
- `prompts/diagnostic_v2.md` : consigne du modèle, version 2, figée, version par défaut (texte brut sans entités HTML, apostrophe ’).
- `sql/schema_diagnostics.json` : schéma de la table BigQuery.
- `sql/audit.sql` : requêtes d’audit et de suivi des coûts.
- `tests/fakes.py` : doublures des ports et réponses de référence.
- `tests/test_architecture.py` : règle de dépendance de l’hexagone.
- `tests/test_config.py` : refus d’une configuration invalide au démarrage.
- `tests/test_map.py` : vérifie que cette carte est à jour.
