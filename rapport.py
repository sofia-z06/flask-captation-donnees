"""Génère un rapport des sorties de pièces en interrogeant l'API de l'application.

Usage : python3 rapport.py            (toutes les saisies)
        python3 rapport.py REF-A320    (filtrées sur un opérateur ou une pièce)
L'application Flask doit tourner (python3 app.py).
"""
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime

API = "http://127.0.0.1:5000/api/saisies"


def recuperer_saisies(recherche=""):
    url = API + ("?q=" + urllib.parse.quote(recherche) if recherche else "")
    with urllib.request.urlopen(url) as reponse:  # requête HTTP GET
        return json.load(reponse)


def main():
    recherche = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        saisies = recuperer_saisies(recherche)
    except OSError:
        sys.exit("Impossible de joindre l'API : lancez d'abord `python3 app.py`.")

    par_piece = defaultdict(int)
    par_operateur = defaultdict(int)
    for s in saisies:
        par_piece[s["piece"]] += int(s["quantite"])
        par_operateur[s["operateur"]] += int(s["quantite"])

    lignes = [
        f"RAPPORT DES SORTIES DE PIÈCES — {datetime.now():%d/%m/%Y %H:%M}",
        f"Filtre : {recherche or 'aucun'} · {len(saisies)} saisie(s)",
        "",
        "Total par pièce :",
        *[f"  {p:<20} {q:>6}" for p, q in sorted(par_piece.items(), key=lambda x: -x[1])],
        "",
        "Total par opérateur :",
        *[f"  {o:<20} {q:>6}" for o, q in sorted(par_operateur.items(), key=lambda x: -x[1])],
    ]
    texte = "\n".join(lignes)
    print(texte)

    nom = f"rapport_{datetime.now():%Y%m%d_%H%M}.txt"
    with open(nom, "w", encoding="utf-8") as f:
        f.write(texte + "\n")
    print(f"\nRapport enregistré dans {nom}")


if __name__ == "__main__":
    main()