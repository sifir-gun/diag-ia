---
name: nouvelle-version-prompt
description: Procédure pour modifier la consigne envoyée au modèle sans casser la traçabilité des diagnostics existants. À utiliser dès qu’on veut changer le ton, les règles ou le format des recommandations.
---

# Créer une nouvelle version du prompt

1. **Ne jamais modifier une version existante.** Chaque diagnostic enregistre l’empreinte exacte du prompt utilisé : réécrire `diagnostic_v1.md` rendrait les anciens diagnostics invérifiables.
2. **Copier la dernière version** vers `prompts/diagnostic_vN.md` (N = dernier numéro + 1) et y faire les changements.
3. **Si le format de sortie change**, mettre à jour le schéma de l’adaptateur Gemini (`adapters/outbound/llm/gemini.py`) et les règles de `domain/advice.py`, avec leurs tests.
4. **Changer la version par défaut** dans `app/config.py` (`PROMPT_VERSION`), dans `.env.example`, et dans `cloudbuild.yaml` si une variable de déploiement la fixe.
5. **Tester en local avec le vrai modèle** sur 3 jeux de réponses contrastés (débutant, en démarrage, avancé) et comparer les recommandations avec la version précédente.
6. **Vérifier** : `pytest -q`, puis relecture par le sous-agent `architecture-reviewer`.
7. **Tracer la décision** : une ligne dans `PLAN.md` qui dit ce qui change et pourquoi.
8. **Figer la version** : ajouter son sha256 dans `PUBLISHED` de `tests/adapters/test_prompts.py` (le même que la colonne `prompt_sha256` des diagnostics réels de l’étape 5), et une règle `Edit(prompts/diagnostic_vN.md)` dans `permissions.deny` de `.claude/settings.json`.
