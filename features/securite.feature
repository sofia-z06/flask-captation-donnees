# language: fr
Fonctionnalité: Sécurité de la démo en ligne
  En tant que propriétaire de l'outil mis en ligne
  Je veux que personne ne puisse altérer les données ou piéger les utilisateurs
  Afin de pouvoir partager la démo en toute confiance

  Scénario: ANO-002 | Une formule Excel est neutralisée à l'export
    Étant donné les saisies suivantes :
      | operateur  | piece  | quantite |
      | =1+1       | VIS-M4 | 3        |
    Quand j'exporte les saisies
    Alors la cellule exportée vaut "'=1+1"

  Scénario: Un champ trop long est refusé
    Étant donné qu'aucune saisie n'est enregistrée
    Quand je déclare une sortie avec un opérateur de 41 caractères
    Alors la saisie est refusée avec le message "limités à 40 caractères"
    Et aucune saisie n'est enregistrée

  Scénario: En démo, les saisies d'un visiteur ne sont pas visibles par les autres
    Étant donné l'application est en mode démo
    Quand un premier visiteur déclare une sortie de 5 pièces "PIECE-SECRETE"
    Alors le premier visiteur voit la pièce "PIECE-SECRETE"
    Et un second visiteur ne voit pas la pièce "PIECE-SECRETE"

  Scénario: En démo, le nombre de saisies par visiteur est limité
    Étant donné l'application est en mode démo
    Quand un visiteur enregistre 21 saisies
    Alors la dernière saisie est refusée avec le message "limitée à 20 saisies"

  Scénario: Les en-têtes de sécurité HTTP sont présents
    Quand je recherche "test"
    Alors la réponse contient l'en-tête de sécurité "Content-Security-Policy"
    Et la réponse contient l'en-tête de sécurité "X-Frame-Options"
