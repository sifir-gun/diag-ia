---
paths:
  - "app/adapters/**/*.py"
  - "app/bootstrap.py"
  - "tests/adapters/**/*.py"
---

# Règles pour les adaptateurs

- Un adaptateur implémente un port de `application/ports.py` et traduit vers ou depuis les objets du domaine. Aucun type d’un SDK ne sort de l’adaptateur.
- Les imports de SDK Google se font dans le constructeur ou la méthode, pas en haut du fichier : les tests n’ont pas besoin des SDK.
- Un adaptateur d’entrée n’importe jamais un adaptateur de sortie. Le partage passe par `adapters/shared`.
- Toute modification de `persistence/rows.py` doit garder `test_row_round_trip_as_bigquery_returns_it` vert et rester alignée avec `sql/schema_diagnostics.json`.
- Le choix entre adaptateur réel et local se fait uniquement dans `bootstrap.py`, selon la configuration.
