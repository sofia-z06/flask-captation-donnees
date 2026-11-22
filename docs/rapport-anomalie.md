# ANO-001 | Saisies invalides acceptées par le serveur

| Champ | Valeur |
|---|---|
| **Statut** | ✅ Corrigée |
| **Sévérité** | Majeure (données fausses enregistrées) |
| **Priorité** | Haute |
| **User story** | US-01 - Déclarer une sortie de pièce |
| **Détectée par** | Scénarios CT-02 à CT-06 (`features/saisie.feature`) |
| **Environnement** | Local - Python 3, Flask 3 |

## Description
Le formulaire HTML impose une quantité ≥ 1 (`min="1"`) et des champs obligatoires
(`required`), mais **le serveur ne vérifiait rien**. En envoyant la requête directement
(outil tiers, script, navigateur modifié), on pouvait enregistrer des données incohérentes.

## Étapes pour reproduire
1. Lancer l'application (`python3 app.py`).
2. Envoyer une requête `POST /` avec `operateur=Test`, `piece=X`, `quantite=-5`
   (par exemple avec le test client Flask, `curl` ou Postman).
3. Ouvrir la page d'accueil.

## Résultat attendu
La saisie est refusée avec un message clair, et rien n'est enregistré.

## Résultat obtenu
La saisie est enregistrée : une ligne avec la quantité **-5** apparaît dans le tableau.
Même comportement avec une quantité `abc` ou un opérateur composé uniquement d'espaces.

## Analyse
La validation reposait uniquement sur le navigateur. Une validation côté client améliore
le confort de l'utilisateur mais ne protège pas les données : **la règle doit être vérifiée
côté serveur**.

## Correction
Ajout d'une fonction `valider()` dans `app.py` :
- opérateur et pièce obligatoires (espaces seuls refusés) ;
- quantité entière ≥ 1 ;
- en cas d'erreur : code HTTP **400**, message affiché, **rien n'est enregistré**.

## Vérification
Les 5 scénarios concernés passent désormais ; la campagne complète est au vert
(13/13 scénarios). Voir [plan-de-test.md](plan-de-test.md).
