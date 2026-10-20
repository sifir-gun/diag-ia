# Diagnostic de maturité IA

Application web : un dirigeant de PME répond à 10 questions et reçoit un score de maturité IA sur 100, plus 3 priorités chiffrées avec un niveau de confiance. FastAPI en architecture hexagonale, déployée sur Cloud Run, Gemini pour les recommandations, BigQuery pour la traçabilité.

Ce fichier est lu par tous les assistants de code (Claude Code via CLAUDE.md, Cursor, Codex).

## Commandes

- Installer : `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt`
- Tests : `.venv/bin/python -m pytest -q`. Ils doivent passer avant chaque commit. Ne pas lancer le `pytest` du PATH : c’est un shim pyenv qui pointe vers un Python 3.11 sans les dépendances du projet (google-genai absent), et il donne de faux échecs.
- Serveur local sans GCP : `LLM_BACKEND=fake STORE_BACKEND=memory uvicorn app.main:app --reload`
- Vérifier un diagnostic stocké : `python -m app.verify <référence>`

## Carte

`MAP.md` indique quels fichiers toucher pour chaque type de changement, et à quoi sert chaque fichier. Lis-le avant de modifier le code, et mets-le à jour quand tu ajoutes, déplaces ou supprimes un module : `tests/test_map.py` échoue sinon.

## Architecture hexagonale

- `app/domain` : règles métier, bibliothèque standard uniquement.
- `app/application` : cas d’usage et ports. Dépend du domaine seulement.
- `app/adapters/inbound` : web FastAPI et ligne de commande.
- `app/adapters/outbound` : Gemini, BigQuery, logs, prompts, horloge.
- `app/bootstrap.py` : seul endroit qui choisit les adaptateurs.

La règle de dépendance est vérifiée par `tests/test_architecture.py`. Ne jamais contourner ce test.

## Règles métier à ne pas casser

- Le score vient de la grille `domain/scoring.py`, jamais du modèle.
- Aucun résultat n’est affiché sans enregistrement réussi.
- Tout ce qui est montré à l’utilisateur est couvert par les empreintes de `domain/fingerprint.py`.
- Une version de prompt publiée n’est jamais modifiée : on en crée une nouvelle.
- L’e-mail du visiteur n’apparaît jamais dans les logs ni dans les événements.
- Chaque nouvelle règle métier a son test.

## Google Cloud

- Projet `wengraf-diag-ia`. Cloud Run `diag-ia` et Artifact Registry `diag-repo` en `europe-west1`, BigQuery en `EU`, Gemini en `global`.
- Comptes de service : `diag-app` pour l’exécution, `diag-build` pour Cloud Build.
- Aucune commande qui crée, modifie ou supprime une ressource cloud sans validation humaine.

## Style

- Textes visibles par l’utilisateur en français, avec apostrophes typographiques (’).
- Jamais de tiret cadratin.
