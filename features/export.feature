# language: fr
Fonctionnalité: US-03 | Exporter les données
  En tant que responsable d'atelier
  Je veux télécharger les saisies au format CSV
  Afin de les exploiter dans Excel

  Contexte:
    Étant donné les saisies suivantes :
      | operateur | piece        | quantite |
      | M. Durand | VIS-M4-INOX  | 40       |
      | L. Martin | CONN-SUBD-15 | 8        |

  Scénario: Export complet
    Quand j'exporte les saisies
    Alors le fichier CSV commence par l'en-tête "date;operateur;piece;quantite"
    Et le fichier CSV contient 2 lignes de données

  Scénario: L'export respecte le filtre
    Quand j'exporte les saisies filtrées sur "martin"
    Alors le fichier CSV contient 1 lignes de données
