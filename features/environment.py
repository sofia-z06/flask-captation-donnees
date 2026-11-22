"""Préparation des tests : chaque scénario utilise un fichier CSV temporaire et vide,
pour ne jamais toucher aux vraies données (saisies.csv)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app  # noqa: E402


def before_scenario(context, scenario):
    fd, chemin = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    os.remove(chemin)  # le fichier n'existe pas au départ : aucune saisie
    app.config["FICHIER"] = chemin
    app.config["TESTING"] = True
    app.config["DEMO"] = False
    context.fichier = chemin
    context.client = app.test_client()


def after_scenario(context, scenario):
    if os.path.exists(context.fichier):
        os.remove(context.fichier)
