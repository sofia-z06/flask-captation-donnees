import csv
import io
import os
import secrets
from datetime import datetime

from flask import Flask, Response, jsonify, redirect, render_template_string, request, session

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# En local : les saisies sont enregistrées dans un fichier CSV partagé.
# En ligne (DEMO_MODE=1) : chaque visiteur a ses propres saisies, stockées dans
# sa session ; personne ne peut modifier ce que voient les autres visiteurs.
app.config["FICHIER"] = "saisies.csv"
app.config["DEMO"] = os.environ.get("DEMO_MODE") == "1"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024          # requêtes de 16 Ko maximum
app.config["SESSION_COOKIE_HTTPONLY"] = True          # cookie inaccessible au JavaScript
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"         # cookie non envoyé par un formulaire d'un autre site
app.config["SESSION_COOKIE_SECURE"] = app.config["DEMO"]  # en ligne : cookie envoyé uniquement en HTTPS
# Clé secrète lue dans l'environnement (générée par Render), jamais écrite dans le code.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

COLONNES = ["date", "operateur", "piece", "quantite"]
LONGUEUR_MAX = 40          # caractères maximum par champ texte
QUANTITE_MAX = 100000
SAISIES_MAX_DEMO = 20      # saisies maximum par visiteur en mode démo

DONNEES_DEMO = [
    {"date": "15/11/2026 13:28", "operateur": "M. Durand", "piece": "VIS-M4-INOX", "quantite": "40"},
    {"date": "15/11/2026 13:29", "operateur": "L. Martin", "piece": "CONN-SUBD-15", "quantite": "8"},
    {"date": "15/11/2026 13:29", "operateur": "S. Bernard", "piece": "FIX-PANNEAU-SOL", "quantite": "4"},
    {"date": "15/11/2026 13:29", "operateur": "M. Durand", "piece": "CONN-SUBD-15", "quantite": "6"},
    {"date": "15/11/2026 13:29", "operateur": "A. Petit", "piece": "ISOL-MLI-02", "quantite": "3"},
    {"date": "15/11/2026 13:29", "operateur": "L. Martin", "piece": "VIS-M4-INOX", "quantite": "25"},
]


# ---------------------------------------------------------------------------
# Stockage
# ---------------------------------------------------------------------------
def lire_saisies():
    """Renvoie la liste des saisies (dictionnaires)."""
    if app.config["DEMO"]:
        return DONNEES_DEMO + session.get("saisies", [])
    fichier = app.config["FICHIER"]
    if not os.path.exists(fichier):
        return []
    with open(fichier, newline="", encoding="utf-8") as f:
        return [dict(zip(COLONNES, ligne)) for ligne in csv.reader(f) if ligne]


def ajouter_saisie(donnees):
    """Enregistre une saisie validée. Renvoie un message d'erreur ou None."""
    ligne = {"date": datetime.now().strftime("%d/%m/%Y %H:%M"),
             "operateur": donnees["operateur"], "piece": donnees["piece"],
             "quantite": str(donnees["quantite"])}
    if app.config["DEMO"]:
        mes_saisies = session.get("saisies", [])
        if len(mes_saisies) >= SAISIES_MAX_DEMO:
            return f"Démo limitée à {SAISIES_MAX_DEMO} saisies par visiteur."
        session["saisies"] = mes_saisies + [ligne]
        return None
    with open(app.config["FICHIER"], "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ligne[c] for c in COLONNES])
    return None


# ---------------------------------------------------------------------------
# Règles métier
# ---------------------------------------------------------------------------
def valider(form):
    """Vérifie une saisie côté serveur. Renvoie (données, erreur).

    ANO-001 : la contrainte min=1 du formulaire HTML pouvait être contournée ;
    le serveur acceptait des quantités négatives, non numériques et des champs vides.
    """
    operateur = form.get("operateur", "").strip()
    piece = form.get("piece", "").strip()
    quantite = form.get("quantite", "").strip()
    if not operateur or not piece:
        return None, "L'opérateur et la référence pièce sont obligatoires."
    if len(operateur) > LONGUEUR_MAX or len(piece) > LONGUEUR_MAX:
        return None, f"L'opérateur et la référence pièce sont limités à {LONGUEUR_MAX} caractères."
    if any(not c.isprintable() for c in operateur + piece):
        return None, "Caractères non autorisés."
    if not quantite.isdigit() or not 1 <= int(quantite) <= QUANTITE_MAX:
        return None, "La quantité doit être un nombre entier supérieur ou égal à 1."
    return {"operateur": operateur, "piece": piece, "quantite": int(quantite)}, None


def filtrer(saisies, recherche):
    """Garde les saisies dont l'opérateur ou la pièce contient le texte recherché."""
    if not recherche:
        return saisies
    r = recherche.lower()
    return [s for s in saisies if r in s["operateur"].lower() or r in s["piece"].lower()]


def neutraliser_formule(valeur):
    """ANO-002 : empêche l'injection de formules dans Excel (« CSV injection »).

    Une cellule commençant par =, +, -, @, tabulation ou retour chariot pourrait être
    exécutée comme une formule à l'ouverture de l'export : on la préfixe d'une apostrophe.
    """
    valeur = str(valeur)
    return "'" + valeur if valeur[:1] in ("=", "+", "-", "@", "\t", "\r") else valeur


# ---------------------------------------------------------------------------
# Sécurité HTTP
# ---------------------------------------------------------------------------
@app.after_request
def entetes_securite(reponse):
    reponse.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
    )
    reponse.headers["X-Content-Type-Options"] = "nosniff"
    reponse.headers["X-Frame-Options"] = "DENY"
    reponse.headers["Referrer-Policy"] = "no-referrer"
    return reponse


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
  td { padding: 10px; border-bottom: 1px solid #eee; word-break: break-word; }
  tr:nth-child(even) td { background: #fafafa; }
  .vide { color: #999; text-align: center; padding: 20px; }
  .erreur { background: #fdecec; color: #b42318; border-radius: 8px; padding: 10px 14px; margin-top: 12px; font-size: 14px; }
  .demo { background: #fff6e0; color: #7a5200; border-radius: 8px; padding: 10px 14px; margin-bottom: 20px; font-size: 13px; }
  .compteur { color: #666; font-size: 13px; margin-top: 8px; }
</style>
</head>
<body>
  {% if demo %}
  <div class="demo">Démo | données fictives. Vos saisies ne sont visibles que par vous et disparaissent à la fin de votre session.</div>
  {% endif %}
  <h1>Déclaration atelier</h1>
  <p>Saisie rapide des sorties de pièces, enregistrées en CSV.</p>

  <form method="post" class="saisie">
    <input name="operateur" placeholder="Opérateur" maxlength="{{ max }}" required>
    <input name="piece" placeholder="Référence pièce" maxlength="{{ max }}" required>
    <input name="quantite" type="number" min="1" max="100000" placeholder="Quantité" required>
    <button>Enregistrer</button>
  </form>
  {% if erreur %}<div class="erreur" role="alert">{{ erreur }}</div>{% endif %}

  <form method="get" class="outils">
    <input name="q" value="{{ q }}" maxlength="{{ max }}" placeholder="Rechercher un opérateur ou une pièce">
    <button class="secondaire">Filtrer</button>
    {% if q %}<a class="btn secondaire" href="/">Effacer</a>{% endif %}
    <a class="btn" href="/export?q={{ q|urlencode }}">Exporter en CSV</a>
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


def afficher(saisies, q="", erreur=None, code=200):
    return render_template_string(PAGE, saisies=saisies, q=q, erreur=erreur,
                                  demo=app.config["DEMO"], max=LONGUEUR_MAX), code


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        donnees, erreur = valider(request.form)
        if not erreur:
            erreur = ajouter_saisie(donnees)
        if erreur:
            # La saisie est refusée : rien n'est enregistré, le message s'affiche.
            return afficher(lire_saisies(), erreur=erreur, code=400)
        return redirect("/")
    q = request.args.get("q", "").strip()[:LONGUEUR_MAX]
    return afficher(filtrer(lire_saisies(), q), q=q)


@app.route("/export")
def export():
    """Télécharge les saisies (filtrées si besoin) au format CSV, lisible dans Excel."""
    saisies = filtrer(lire_saisies(), request.args.get("q", "").strip()[:LONGUEUR_MAX])
    sortie = io.StringIO()
    writer = csv.DictWriter(sortie, fieldnames=COLONNES, delimiter=";")
    writer.writeheader()
    writer.writerows({c: neutraliser_formule(s[c]) for c in COLONNES} for s in saisies)
    return Response(
        "﻿" + sortie.getvalue(),  # BOM pour que Excel lise bien les accents
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=saisies_atelier.csv"},
    )


@app.route("/api/saisies")
def api_saisies():
    """API JSON : liste des saisies, filtrable avec ?q=..."""
    saisies = filtrer(lire_saisies(), request.args.get("q", "").strip()[:LONGUEUR_MAX])
    return jsonify(saisies)


if __name__ == "__main__":
    # Mode debug uniquement en local ; en ligne, l'application est lancée par gunicorn.
    app.run(debug=True, port=5000)
