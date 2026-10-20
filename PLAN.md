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
- [ ] Faire un diagnostic réel avec `LLM_BACKEND=vertex` et `STORE_BACKEND=bigquery`
- [ ] Vérifier la ligne avec `python -m app.verify`

## Phase 4. Déploiement
- [ ] Créer le compte de service `diag-build` et ses rôles
- [ ] (Guney, console) Connecter GitHub et créer le déclencheur Cloud Build sur `main`
- [ ] Premier déploiement réussi, URL Cloud Run notée ici :

## Phase 5. Observabilité
- [ ] Créer le dataset `audit_logs` et le sink `diag-audit`
- [ ] Vérifier les 3 requêtes de `sql/audit.sql` sur des diagnostics réels
- [ ] (Guney, navigateur) Tableau de bord Looker Studio
- [ ] Mesurer le coût réel par diagnostic et le noter dans le README

## Phase 6. Vitrine
- [ ] Captures du formulaire, d’un résultat et du tableau de bord dans le README
- [ ] Mettre à jour le CV et les profils
- [ ] Préparer les 3 réponses d’entretien : services et pourquoi, droits et secrets, coût

## Bonus
- [ ] Limitation par adresse IP sur le formulaire
- [ ] Chaîne de hachage entre diagnostics
- [ ] Infrastructure en Terraform
