@AGENTS.md

## Spécifique à Claude Code

- Avant une nouvelle fonctionnalité, lis `SPEC.md`. Si la demande sort du périmètre, dis-le avant de coder.
- `PLAN.md` dit où en est le projet. Coche une tâche dès qu’elle est terminée et vérifiée.
- Avant chaque commit qui touche `app/`, fais relire le changement par le sous-agent `architecture-reviewer`.
- Pour ajouter un service externe, utilise le skill `nouveau-port`. Pour changer le prompt, le skill `nouvelle-version-prompt`.
- Montre chaque commande `gcloud` ou `bq` qui crée, modifie ou supprime une ressource, et attends mon accord.
- Un hook relance les tests quand tu termines une réponse qui a modifié du code. S’il échoue, corrige avant de conclure.
