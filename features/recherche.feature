# language: fr
Fonctionnalité: US-02 | Retrouver une saisie
  En tant que responsable d'atelier
  Je veux filtrer les saisies par opérateur ou par pièce
  Afin de retrouver rapidement une information

  Contexte:
    Étant donné les saisies suivantes :
      | operateur | piece        | quantite |
      | M. Durand | VIS-M4-INOX  | 40       |
      | L. Martin | CONN-SUBD-15 | 8        |
      | M. Durand | CONN-SUBD-15 | 6        |

  Scénario: Filtrer par opérateur sans tenir compte des majuscules
    Quand je recherche "durand"
    Alors 2 saisies sont affichées
    Et le compteur indique "2 saisie(s)"

  Scénario: Filtrer par référence pièce
    Quand je recherche "CONN"
    Alors 2 saisies sont affichées

  Scénario: Recherche sans résultat
    Quand je recherche "inconnu"
    Alors 0 saisies sont affichées
