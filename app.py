import csv
import io
import os
from datetime import datetime

from flask import Flask, Response, jsonify, redirect, render_template_string, request

app = Flask(__name__)
app.config["FICHIER"] = "saisies.csv"  # modifiable (les tests utilisent un fichier temporaire)
COLONNES = ["date", "operateur", "piece", "quantite"]


def lire_saisies():
    """Lit le CSV et renvoie une liste de dictionnaires."""
    fichier = app.config["FICHIER"]
    if not os.path.exists(fichier):
        return []
    with open(fichier, newline="", encoding="utf-8") as f:
        return [dict(zip(COLONNES, ligne)) for ligne in csv.reader(f) if ligne]


def valider(form):
    """Vérifie une saisie côté serveur. Renvoie (données, erreur).

    Correction de l'anomalie ANO-001 : la contrainte min=1 du formulaire HTML
    pouvait être contournée ; le serveur acceptait des quantités négatives,
    non numériques et des champs vides.
    """
    operateur = form.get("operateur", "").strip()
    piece = form.get("piece", "").strip()
    quantite = form.get("quantite", "").strip()
    if not operateur or not piece:
        return None, "L'opérateur et la référence pièce sont obligatoires."
    if not quantite.isdigit() or int(quantite) < 1:
        return None, "La quantité doit être un nombre entier supérieur ou égal à 1."
    return {"operateur": operateur, "piece": piece, "quantite": int(quantite)}, None


def filtrer(saisies, recherche):
    """Garde les saisies dont l'opérateur ou la pièce contient le texte recherché."""
    if not recherche:
        return saisies
    r = recherche.lower()
    return [s for s in saisies if r in s["operateur"].lower() or r in s["piece"].lower()]


PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Captation atelier</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 16px; color: #222; }
  h1 { font-size: 24px; margin-bottom: 4px; }
  p { color: #666; margin-top: 0; }
  form { display: flex; gap: 8px; flex-wrap: wrap; }
  .saisie { background: #f5f6f8; padding: 16px; border-radius: 10px; }
  .outils { margin-top: 24px; align-items: center; }
  input { flex: 1; min-width: 140px; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
  button, .btn { padding: 10px 18px; border: none; border-radius: 6px; background: #1f4e9c; color: white;
                 font-weight: 600; cursor: pointer; text-decoration: none; font-size: 14px; }
  button:hover, .btn:hover { background: #163a75; }
  .secondaire { background: #e4e8f0; color: #1f4e9c; }
  .secondaire:hover { background: #d3d9e6; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }
  th { text-align: left; background: #1f4e9c; color: white; padding: 10px; }
  td { padding: 10px; border-bottom: 1px solid #eee; }
  tr:nth-child(even) td { background: #fafafa; }
  .vide { color: #999; text-align: center; padding: 20px; }
  .erreur { background: #fdecec; color: #b42318; border-radius: 8px; padding: 10px 14px; margin-top: 12px; font-size: 14px; }
  .compteur { color: #666; font-size: 13px; margin-top: 8px; }
</style>
</head>
<body>
  <h1>Déclaration atelier</h1>
  <p>Saisie rapide des sorties de pièces, enregistrées en CSV.</p>

  <form method="post" class="saisie">
    <input name="operateur" placeholder="Opérateur" required>
    <input name="piece" placeholder="Référence pièce" required>
    <input name="quantite" type="number" min="1" placeholder="Quantité" required>
    <button>Enregistrer</button>
  </form>
  {% if erreur %}<div class="erreur" role="alert">{{ erreur }}</div>{% endif %}

  <form method="get" class="outils">
    <input name="q" value="{{ q }}" placeholder="Rechercher un opérateur ou une pièce">
    <button class="secondaire">Filtrer</button>
    {% if q %}<a class="btn secondaire" href="/">Effacer</a>{% endif %}
    <a class="btn" href="/export?q={{ q }}">Exporter en CSV</a>
  </form>

  <div class="compteur">{{ saisies|length }} saisie(s){% if q %} pour « {{ q }} »{% endif %}</div>

  <table>
    <tr><th>Date</th><th>Opérateur</th><th>Pièce</th><th>Quantité</th></tr>
    {% for s in saisies|reverse %}
      <tr><td>{{ s.date }}</td><td>{{ s.operateur }}</td><td>{{ s.piece }}</td><td>{{ s.quantite }}</td></tr>
    {% else %}
      <tr><td colspan="4" class="vide">Aucune saisie</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        donnees, erreur = valider(request.form)
        if erreur:
            # La saisie est refusée : rien n'est enregistré, le message s'affiche.
            return render_template_string(PAGE, saisies=lire_saisies(), q="", erreur=erreur), 400
        with open(app.config["FICHIER"], "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                donnees["operateur"],
                donnees["piece"],
                donnees["quantite"],
            ])
        return redirect("/")
    q = request.args.get("q", "").strip()
    return render_template_string(PAGE, saisies=filtrer(lire_saisies(), q), q=q, erreur=None)


@app.route("/export")
def export():
    """Télécharge les saisies (filtrées si besoin) au format CSV, lisible dans Excel."""
    saisies = filtrer(lire_saisies(), request.args.get("q", "").strip())
    sortie = io.StringIO()
    writer = csv.DictWriter(sortie, fieldnames=COLONNES, delimiter=";")
    writer.writeheader()
    writer.writerows(saisies)
    return Response(
        "﻿" + sortie.getvalue(),  # BOM pour que Excel lise bien les accents
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=saisies_atelier.csv"},
    )


@app.route("/api/saisies")
def api_saisies():
    """API JSON : liste des saisies, filtrable avec ?q=..."""
    saisies = filtrer(lire_saisies(), request.args.get("q", "").strip())
    return jsonify(saisies)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
