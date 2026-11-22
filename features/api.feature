# language: fr
Fonctionnalité: US-04 | Récupérer les données par API
  En tant qu'outil tiers
  Je veux interroger une API JSON
  Afin d'automatiser des rapports

  Contexte:
    Étant donné les saisies suivantes :
      | operateur | piece        | quantite |
      | M. Durand | VIS-M4-INOX  | 40       |
      | L. Martin | CONN-SUBD-15 | 8        |

  Scénario: Lister toutes les saisies
    Quand j'appelle l'API "/api/saisies"
    Alors la réponse est un JSON de 2 saisies

  Scénario: Filtrer via l'API
    Quand j'appelle l'API "/api/saisies?q=VIS"
    Alors la réponse est un JSON de 1 saisies
    Et la première saisie concerne l'opérateur "M. Durand"
