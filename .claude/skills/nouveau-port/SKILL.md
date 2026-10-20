---
name: nouveau-port
description: Procédure pour brancher un nouveau service externe (base de données, file de messages, limiteur de débit, autre modèle d’IA) sans casser l’architecture hexagonale. À utiliser dès qu’une fonctionnalité a besoin de parler à quelque chose en dehors de l’application.
---

# Ajouter un port et ses adaptateurs

1. **Définir le besoin en termes métier.** Nomme le port d’après ce dont le cas d’usage a besoin (`RateLimiter`, `LeadNotifier`), jamais d’après la technologie (`RedisClient`).
2. **Déclarer le port** dans `app/application/ports.py` : un `Protocol` avec les méthodes minimales, et des types d’entrée et de sortie du domaine ou des dataclasses de `ports.py`.
3. **Écrire d’abord le test du cas d’usage** dans `tests/application/`, avec une doublure du port dans `tests/fakes.py`. Le test doit couvrir le cas nominal et l’échec du service.
4. **Brancher le port dans le cas d’usage** par son constructeur. Traduire les erreurs du service en erreur d’application et publier un événement.
5. **Écrire l’adaptateur réel** dans `app/adapters/outbound/<domaine>/`. Import du SDK dans le constructeur. Traduction complète vers les objets du domaine.
6. **Écrire l’adaptateur local** (mémoire ou faux) pour le développement sans réseau.
7. **Choisir l’adaptateur dans `app/bootstrap.py`** selon une variable de configuration ajoutée à `app/config.py` et à `.env.example`.
8. **Vérifier** : `pytest -q`, puis faire relire par le sous-agent `architecture-reviewer`.
9. **Documenter** : une ligne dans le tableau des ports du README, les nouveaux fichiers dans `MAP.md`, et la tâche cochée dans `PLAN.md`.
