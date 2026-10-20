---
paths:
  - "app/domain/**/*.py"
  - "tests/domain/**/*.py"
---

# Règles pour le domaine

- Bibliothèque standard uniquement : pas de Pydantic, pas de FastAPI, pas de SDK, pas d’accès réseau ni disque.
- Entités et objets-valeurs en `@dataclass(frozen=True)`. On ne modifie pas un objet, on en crée un autre avec `dataclasses.replace`.
- Une règle métier lève une exception du domaine (`InvalidSubmission`, `InvalidAdvice`), jamais une erreur HTTP.
- Toute modification de ce qui est affiché à l’utilisateur doit passer par `shown_document` dans `fingerprint.py`, sinon les empreintes ne protègent plus le résultat.
- Une option ajoutée à une question notée dans `scoring.py` doit recevoir un poids : `test_every_scored_option_has_a_weight` le vérifie.
