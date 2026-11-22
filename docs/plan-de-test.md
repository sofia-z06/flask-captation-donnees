# Plan de test

## Objectif
Vérifier que l'outil de captation répond aux user stories US-01 à US-04
(voir [user-stories.md](user-stories.md)), et qu'aucune donnée invalide ne peut être enregistrée.

## Périmètre
| Inclus | Exclu |
|---|---|
| Saisie et validation côté serveur | Performance / montée en charge |
| Recherche / filtre | Compatibilité navigateurs |
| Export CSV | Authentification (non prévue à ce stade) |
| Sécurité de la démo en ligne | |
| API JSON | |

## Approche
- **Tests fonctionnels automatisés en BDD** : scénarios écrits en Gherkin (français),
  exécutés avec `behave` (équivalent Python de Cucumber), dans `features/`.
- Chaque scénario part d'un **jeu de données isolé** (fichier CSV temporaire) :
  les tests ne touchent jamais aux vraies données.
- **Cas nominaux** (ce qui doit marcher) et **cas d'erreur** (ce qui doit être refusé),
  avec un « Plan du scénario » pour tester plusieurs valeurs invalides d'un coup.

## Cas de test
| ID | User story | Scénario | Type | Résultat |
|---|---|---|---|---|
| CT-01 | US-01 | Saisie valide enregistrée et affichée en premier | Nominal | ✅ |
| CT-02 | US-01 | Quantité -5 refusée | Erreur | ✅ (❌ avant correction ANO-001) |
| CT-03 | US-01 | Quantité 0 refusée | Erreur | ✅ (❌ avant correction ANO-001) |
| CT-04 | US-01 | Quantité « abc » refusée | Erreur | ✅ (❌ avant correction ANO-001) |
| CT-05 | US-01 | Quantité 2.5 refusée | Erreur | ✅ (❌ avant correction ANO-001) |
| CT-06 | US-01 | Opérateur vide refusé | Erreur | ✅ (❌ avant correction ANO-001) |
| CT-07 | US-02 | Filtre par opérateur, insensible à la casse | Nominal | ✅ |
| CT-08 | US-02 | Filtre par référence pièce | Nominal | ✅ |
| CT-09 | US-02 | Recherche sans résultat | Limite | ✅ |
| CT-10 | US-03 | Export complet avec en-tête | Nominal | ✅ |
| CT-11 | US-03 | Export respectant le filtre | Nominal | ✅ |
| CT-12 | US-04 | API : liste complète | Nominal | ✅ |
| CT-13 | US-04 | API : filtre `?q=` | Nominal | ✅ |
| CT-14 | US-03 | Formule Excel neutralisée à l'export | Sécurité | ✅ (corrige ANO-002) |
| CT-15 | US-01 | Champ de plus de 40 caractères refusé | Sécurité | ✅ |
| CT-16 | Démo | Saisies d'un visiteur invisibles pour les autres | Sécurité | ✅ |
| CT-17 | Démo | Limite de 20 saisies par visiteur | Sécurité | ✅ |
| CT-18 | Toutes | En-têtes de sécurité HTTP présents | Sécurité | ✅ |

## Bilan de la campagne
- **Première exécution** : 8 scénarios réussis, **5 en échec** → anomalie
  [ANO-001](rapport-anomalie.md) ouverte.
- **Après correction** : **13 scénarios sur 13 réussis**, 49 étapes.
- **Revue de sécurité avant mise en ligne** : anomalie [ANO-002](rapport-anomalie.md) corrigée et 5 scénarios de sécurité ajoutés : **18 scénarios sur 18 réussis**, 66 étapes.

## Lancer les tests
```bash
pip install -r requirements.txt
behave --lang fr
```
