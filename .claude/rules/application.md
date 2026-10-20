---
paths:
  - "app/application/**/*.py"
  - "tests/application/**/*.py"
---

# Règles pour les cas d’usage

- Un cas d’usage reçoit ses dépendances par son constructeur, sous forme de ports. Il n’instancie jamais un adaptateur.
- Ordre de `RunDiagnostic` à préserver : validation, score, appel au modèle, contrôle du conseil, empreintes, enregistrement, événement. L’enregistrement précède toujours le retour du résultat.
- Les erreurs des adaptateurs sont traduites en erreurs d’application (`AdviceUnavailable`, `DiagnosticNotRecorded`) et publiées comme événement.
- Les événements ne contiennent jamais l’e-mail ni le texte libre du visiteur.
- Les tests utilisent les doublures de `tests/fakes.py` : horloge fixe, identifiants séquentiels, événements enregistrés.
