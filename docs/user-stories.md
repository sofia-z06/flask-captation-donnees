# Expression du besoin et user stories

## Contexte

Dans un atelier, les opérateurs sortent des pièces du stock tout au long de la journée.
Ces sorties étaient notées à la main, ce qui rendait le suivi difficile : informations
manquantes, quantités illisibles, aucune vue d'ensemble pour le responsable.

**Objectif :** permettre aux opérateurs, qui ne sont pas informaticiens, de déclarer une
sortie de pièce en quelques secondes, et au responsable de retrouver, exporter et
analyser ces données.

## Utilisateurs

| Persona | Besoin principal |
|---|---|
| **Opérateur d'atelier** | Déclarer une sortie rapidement, sans formation |
| **Responsable d'atelier** | Retrouver une saisie, exporter les données, obtenir un récapitulatif |
| **Outil tiers** (Excel, script, outil d'analyse) | Récupérer les données dans un format standard |

## User stories

### US-01 | Déclarer une sortie de pièce
**En tant qu'** opérateur d'atelier,
**je veux** enregistrer une sortie de pièce (opérateur, référence, quantité),
**afin de** garder une trace fiable sans papier.

Critères d'acceptation :
- Une saisie complète et valide est enregistrée avec la date et l'heure.
- La nouvelle saisie apparaît en haut du tableau.
- Si un champ obligatoire est vide, la saisie est refusée avec un message clair.
- Si la quantité n'est pas un entier ≥ 1, la saisie est refusée avec un message clair.
- Une saisie refusée n'est jamais enregistrée.

### US-02 | Retrouver une saisie
**En tant que** responsable d'atelier,
**je veux** filtrer les saisies par opérateur ou par référence pièce,
**afin de** retrouver rapidement une information.

Critères d'acceptation :
- La recherche porte sur l'opérateur et sur la référence pièce.
- La recherche ne tient pas compte des majuscules/minuscules.
- Le nombre de résultats est affiché.

### US-03 | Exporter les données
**En tant que** responsable d'atelier,
**je veux** télécharger les saisies au format CSV,
**afin de** les exploiter dans Excel ou un outil d'analyse.

Critères d'acceptation :
- Le fichier contient une ligne d'en-tête (date ; operateur ; piece ; quantite).
- L'export respecte le filtre en cours.
- Les accents s'affichent correctement dans Excel.

### US-04 | Récupérer les données par API
**En tant qu'** outil tiers,
**je veux** interroger une API JSON,
**afin d'** automatiser des rapports sans passer par l'interface.

Critères d'acceptation :
- `GET /api/saisies` renvoie la liste des saisies en JSON.
- Le paramètre `?q=` filtre les résultats comme dans l'interface.

## Traçabilité

| User story | Scénarios automatisés |
|---|---|
| US-01 | `features/saisie.feature` |
| US-02 | `features/recherche.feature` |
| US-03 | `features/export.feature` |
| US-04 | `features/api.feature` |
