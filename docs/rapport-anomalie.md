# ANO-001 | Saisies invalides acceptées par le serveur

| Champ | Valeur |
|---|---|
| **Statut** | ✅ Corrigée |
| **Sévérité** | Majeure (données fausses enregistrées) |
| **Priorité** | Haute |
| **User story** | US-01 : Déclarer une sortie de pièce |
| **Détectée par** | Scénarios CT-02 à CT-06 (`features/saisie.feature`) |
| **Environnement** | Local, Python 3, Flask 3 |

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

---

# ANO-002 | Injection de formules dans l'export CSV

| Champ | Valeur |
|---|---|
| **Statut** | ✅ Corrigée |
| **Sévérité** | Majeure (sécurité) |
| **Priorité** | Haute (avant mise en ligne) |
| **User story** | US-03 : Exporter les données |
| **Détectée par** | Revue de sécurité avant déploiement ; scénario ajouté dans `features/securite.feature` |

## Description
Une saisie commençant par `=`, `+`, `-` ou `@` était exportée telle quelle. À l'ouverture
du fichier dans Excel, elle pouvait être interprétée comme une **formule** (attaque connue
sous le nom de « CSV injection » ou « formula injection »).

## Étapes pour reproduire
1. Saisir l'opérateur `=1+1`.
2. Exporter en CSV et ouvrir le fichier dans Excel.

## Résultat attendu
La cellule affiche le texte `=1+1`.

## Résultat obtenu
Excel calcule la formule et affiche `2`.

## Correction
Fonction `neutraliser_formule()` dans `app.py` : toute cellule commençant par un caractère
dangereux est préfixée d'une apostrophe à l'export, ce qui force Excel à l'afficher comme du texte.
