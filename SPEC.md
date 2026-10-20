# Spécification

## Objectif

Donner à un dirigeant de PME, en 3 minutes, un diagnostic de maturité IA crédible et traçable. Le projet sert aussi de vitrine technique : un recruteur doit pouvoir lire le repo et comprendre les choix d’architecture.

## Utilisateurs

- **Le dirigeant** remplit le questionnaire et lit son résultat.
- **Le recruteur ou le client** lit le README et le code.
- **L’auditeur** (Guney) retrouve et vérifie n’importe quel diagnostic.

## Exigences fonctionnelles

- **F1.** Un questionnaire de 10 questions : 8 à choix, 1 à choix multiples sur les outils, 1 texte libre sur la priorité.
- **F2.** Un score sur 100, calculé par une grille fixe, avec son détail par critère et un niveau (Débutant, En démarrage, En structuration, Avancé).
- **F3.** Une synthèse et 3 recommandations classées, chacune avec un gain estimé, un effort et une confiance entre 0 et 1.
- **F4.** Un accord explicite obligatoire avant analyse. Un e-mail facultatif pour être recontacté.
- **F5.** Une page de résultat qui affiche la référence et l’empreinte du diagnostic.
- **F6.** Une API JSON équivalente au formulaire.
- **F7.** Une commande qui vérifie qu’un diagnostic stocké n’a pas été modifié.

## Exigences non fonctionnelles

- **Traçabilité.** Chaque diagnostic est stocké avec ses réponses, sa sortie, le modèle, la version et l’empreinte du prompt, ses tokens, sa latence et son coût.
- **Échec fermé.** Si l’enregistrement échoue, le résultat n’est pas affiché.
- **Sécurité.** Aucune clé API. Comptes de service avec droits minimum. Réponses du visiteur traitées comme des données, jamais comme des consignes.
- **Données personnelles.** L’e-mail n’apparaît jamais dans les logs. Stockage dans l’UE.
- **Coût.** Moins de 5 € par mois à faible trafic. Alerte budget active. 3 instances au maximum.
- **Testabilité.** Tout le cœur se teste sans réseau.

## Hors périmètre

Comptes utilisateurs, paiement, envoi automatique d’e-mails, multilingue, historique des diagnostics côté visiteur.

## Critères d’acceptation de la version 1

- Le formulaire public fonctionne sur l’URL Cloud Run, sur mobile comme sur ordinateur.
- Un diagnostic réel est visible dans BigQuery et passe `python -m app.verify`.
- Ses événements sont visibles dans `audit_logs` et reliés par `diagnostic_id`.
- Un push sur `main` redéploie sans intervention.
- Le coût réel par diagnostic est mesuré et noté dans le README.
