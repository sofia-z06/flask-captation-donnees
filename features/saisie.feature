# language: fr
Fonctionnalité: US-01 | Déclarer une sortie de pièce
  En tant qu'opérateur d'atelier
  Je veux enregistrer une sortie de pièce
  Afin de garder une trace fiable sans papier

  Contexte:
    Étant donné qu'aucune saisie n'est enregistrée

  Scénario: Saisie valide
    Quand je déclare une sortie de 12 pièces "VIS-M4-INOX" pour l'opérateur "M. Durand"
    Alors la saisie est acceptée
    Et le tableau contient 1 saisie
    Et la saisie la plus récente concerne la pièce "VIS-M4-INOX"

  Plan du scénario: Saisie refusée lorsque la quantité est invalide
    Quand je déclare une sortie de "<quantite>" pièces "VIS-M4-INOX" pour l'opérateur "M. Durand"
    Alors la saisie est refusée avec le message "La quantité doit être un nombre entier"
    Et aucune saisie n'est enregistrée

    Exemples:
      | quantite |
      | -5       |
      | 0        |
      | abc      |
      | 2.5      |

  Scénario: Saisie refusée lorsque l'opérateur est vide
    Quand je déclare une sortie de 3 pièces "CONN-SUBD-15" pour l'opérateur "   "
    Alors la saisie est refusée avec le message "obligatoires"
    Et aucune saisie n'est enregistrée
