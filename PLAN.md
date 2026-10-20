# Plan

Coche une tâche quand elle est terminée et vérifiée, avec la date.

## Phase 0. Squelette
- [x] Repo en architecture hexagonale, 56 tests, règle de dépendance testée
- [x] Écosystème Claude Code : AGENTS.md, CLAUDE.md, MAP.md vérifiée par un test, SPEC.md, PLAN.md, règles, sous-agent, skills, hook de tests

## Phase 1. Vérification locale
- [x] Installer le venv et faire passer `pytest -q` (2026-10-20, Python 3.12, 58 tests)
- [x] Lancer le serveur avec les adaptateurs locaux et faire un diagnostic dans le navigateur (2026-10-20)
- [x] Ajuster les questions ou le design si besoin (2026-10-20, aucun changement nécessaire)
- [x] Créer le repo GitHub public `diag-ia` et pousser `main` (2026-10-20, https://github.com/sifir-gun/diag-ia)

## Phase 2. Fondations GCP
- [x] (Guney, console) Créer le projet, lier la facturation, poser l’alerte budget à 5 € (2026-10-20, facturation liée à 0152C9-7D5274-E5751C, budget posé par Guney)
- [x] Activer les APIs (2026-10-20, run, cloudbuild, artifactregistry, bigquery, aiplatform, logging)
- [x] Créer le compte de service `diag-app` et ses trois rôles projet (2026-10-20, aiplatform.user, bigquery.jobUser, logging.logWriter)
- [x] Créer le dépôt Artifact Registry `diag-repo` (2026-10-20, Docker, europe-west1)
- [x] Créer le dataset `diagnostic` et la table `diagnostics` (2026-10-20, EU, partition par jour sur created_at, 19 colonnes conformes au schéma)
- [x] (Guney, console) Donner à `diag-app` le rôle BigQuery Data Editor sur la table `diagnostics` (2026-10-20, posé sur la table plutôt que sur le dataset parce que l’application n’utilise que cette table, droit plus strict)

## Phase 3. Vrais services en local
- [x] Vérifier que `gemini-3.5-flash` répond en location `global`, sinon choisir le Flash le plus récent (2026-10-20, répond, google-genai 2.31.0)
- [x] Faire un diagnostic réel avec `LLM_BACKEND=vertex` et `STORE_BACKEND=bigquery` (2026-10-20, référence 5d75355694604c0c9ec8d73eb0c9614d, 954 tokens en entrée, 2 563 en sortie, 20 s, 0,0245 $)
- [x] Vérifier la ligne avec `python -m app.verify` (2026-10-20, intègre, code de sortie 0)
- [x] Consigne v2 : texte brut sans entités HTML et apostrophe ’, parce que Gemini a renvoyé `&eacute;` en v1, que la page aurait affiché tel quel. L’adaptateur Gemini décode les entités, `normalize_advice` rejette celles qui subsistent et convertit l’apostrophe droite (2026-10-20, 3 diagnostics réels débutant 5, en démarrage 48, avancé 90, textes propres, tous intègres)

## Phase 4. Déploiement
- [x] Créer le compte de service `diag-build` et ses rôles (2026-10-20, run.admin et logging.logWriter sur le projet, artifactregistry.writer sur le dépôt `diag-repo` seulement, iam.serviceAccountUser sur `diag-app` seulement)
- [x] (Guney, console) Connecter GitHub et créer le déclencheur Cloud Build sur `main` (2026-10-20, déclencheur `deploy-main` en europe-west1, connexion 2e génération limitée au dépôt, compte `diag-build`, branche `^main$`, `cloudbuild.yaml` vérifiés avec `gcloud builds triggers describe` ; Secret Manager activé pour le jeton de la connexion)
- [x] Premier déploiement réussi, URL Cloud Run notée ici : https://diag-ia-23ifvkfvfq-ew.a.run.app (2026-10-20, build 284269b0 sur 7997b16, 4 étapes au vert, révision diag-ia-00001-jpc sous diag-app, / et /health répondent 200)

## Phase 5. Observabilité
- [x] La configuration refuse de démarrer si `GCP_PROJECT` est vide avec les adaptateurs réels (`LLM_BACKEND=vertex` ou `STORE_BACKEND=bigquery`), ou si une valeur `PRICE_*` est invalide, avec ses tests. Aujourd’hui le projet vide n’échoue qu’à l’appel BigQuery (404 sur `projects//jobs`) et `_float` remplace en silence une valeur invalide par la valeur par défaut (2026-10-20, fait : valeurs inconnues de `LLM_BACKEND` et `STORE_BACKEND` refusées aussi, `ConfigurationError` levée par `get_settings`, 19 tests dans `tests/test_config.py`)
- [ ] Tester un niveau de réflexion plus bas de Gemini sur les 3 profils (débutant, en démarrage, avancé) : en v2, latence jusqu’à 55 s en local et 74 s en production (diagnostic 3f8e299880bf42e195dd1f7e6073044d, requête `POST /diagnostic`), coût autour de 0,03 $ par diagnostic. Implémentation : variable `THINKING_LEVEL` validée dans `app/config.py`, niveau inscrit dans le champ `model` de chaque diagnostic (par exemple `gemini-3.5-flash/low`), donc couvert par l’empreinte
- [ ] Réessayer automatiquement quand Gemini répond 503 ou 429, au plus 2 fois avec un délai croissant, en publiant un événement à chaque nouvel essai (2 réponses 503 UNAVAILABLE sur 15 appels pendant la mesure du niveau de réflexion du 2026-10-20)
- [ ] Faire ignorer au déclencheur `deploy-main` les fichiers de documentation (`README.md`, `PLAN.md`, `MAP.md`, `SPEC.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/**`), mais pas `prompts/`, qui change le comportement de l’application
- [ ] Créer le dataset `audit_logs` et le sink `diag-audit`
- [ ] Vérifier les 3 requêtes de `sql/audit.sql` sur des diagnostics réels
- [ ] (Guney, navigateur) Tableau de bord Looker Studio
- [ ] Mesurer le coût réel par diagnostic et le noter dans le README
- [ ] Consigne v3 : interdire de reformuler un chiffre des réponses (« Plus de 50 heures » devenu « les 50 heures perdues »), interdire de prendre les exemples d’une option pour des faits (« Usage individuel (ChatGPT, Copilot…) » devenu « un usage individuel de Copilot ») et mieux calibrer la confiance (0,95 jugé trop optimiste)

## Phase 6. Vitrine
- [ ] Captures du formulaire, d’un résultat et du tableau de bord dans le README
- [ ] Mettre à jour le CV et les profils
- [ ] Préparer les 3 réponses d’entretien : services et pourquoi, droits et secrets, coût

## Bonus
- [ ] Limitation par adresse IP sur le formulaire
- [ ] Chaîne de hachage entre diagnostics
- [ ] Infrastructure en Terraform
