"""Définition des étapes Gherkin (l'équivalent des « step definitions » de Cucumber)."""
import csv
import io
import re

from behave import given, then, when


def lignes_tableau(html):
    """Renvoie les lignes de données du tableau HTML (hors en-tête et ligne « Aucune saisie »)."""
    corps = html.split("<table>", 1)[1]
    return [l for l in re.findall(r"<tr>(.*?)</tr>", corps, re.S) if "<td>" in l and 'class="vide"' not in l]


# ---------- Étant donné ----------

@given("aucune saisie n'est enregistrée")
def etape_aucune_saisie(context):
    pass  # assuré par environment.py (fichier temporaire vide)


@given("les saisies suivantes :")
def etape_saisies(context):
    for ligne in context.table:
        reponse = context.client.post("/", data={
            "operateur": ligne["operateur"], "piece": ligne["piece"], "quantite": ligne["quantite"]})
        assert reponse.status_code == 302, f"Préparation impossible : {ligne}"


# ---------- Quand ----------

@when('je déclare une sortie de {quantite:d} pièces "{piece}" pour l\'opérateur "{operateur}"')
def etape_declarer(context, quantite, piece, operateur):
    context.reponse = context.client.post("/", data={
        "operateur": operateur, "piece": piece, "quantite": str(quantite)})


@when('je déclare une sortie de "{quantite}" pièces "{piece}" pour l\'opérateur "{operateur}"')
def etape_declarer_brut(context, quantite, piece, operateur):
    context.reponse = context.client.post("/", data={
        "operateur": operateur, "piece": piece, "quantite": quantite})


@when('je recherche "{texte}"')
def etape_rechercher(context, texte):
    context.reponse = context.client.get("/", query_string={"q": texte})


@when("j'exporte les saisies")
def etape_exporter(context):
    context.reponse = context.client.get("/export")


@when('j\'exporte les saisies filtrées sur "{texte}"')
def etape_exporter_filtre(context, texte):
    context.reponse = context.client.get("/export", query_string={"q": texte})


@when('j\'appelle l\'API "{url}"')
def etape_api(context, url):
    context.reponse = context.client.get(url)


# ---------- Alors ----------

@then("la saisie est acceptée")
def etape_acceptee(context):
    assert context.reponse.status_code == 302, f"Code reçu : {context.reponse.status_code}"


@then('la saisie est refusée avec le message "{message}"')
def etape_refusee(context, message):
    assert context.reponse.status_code == 400, f"Code reçu : {context.reponse.status_code}"
    assert message in context.reponse.get_data(as_text=True), "Message d'erreur absent"


@then("aucune saisie n'est enregistrée")
def etape_rien(context):
    assert lignes_tableau(context.client.get("/").get_data(as_text=True)) == []


@then("le tableau contient {n:d} saisie")
def etape_nb_tableau(context, n):
    assert len(lignes_tableau(context.client.get("/").get_data(as_text=True))) == n


@then('la saisie la plus récente concerne la pièce "{piece}"')
def etape_plus_recente(context, piece):
    premiere = lignes_tableau(context.client.get("/").get_data(as_text=True))[0]
    assert piece in premiere


@then("{n:d} saisies sont affichées")
def etape_nb_affichees(context, n):
    trouvees = len(lignes_tableau(context.reponse.get_data(as_text=True)))
    assert trouvees == n, f"{trouvees} saisie(s) affichée(s) au lieu de {n}"


@then('le compteur indique "{texte}"')
def etape_compteur(context, texte):
    assert texte in context.reponse.get_data(as_text=True)


@then('le fichier CSV commence par l\'en-tête "{entete}"')
def etape_entete(context, entete):
    contenu = context.reponse.get_data(as_text=True).lstrip("﻿")
    assert contenu.splitlines()[0] == entete


@then("le fichier CSV contient {n:d} lignes de données")
def etape_lignes_csv(context, n):
    contenu = context.reponse.get_data(as_text=True).lstrip("﻿")
    lignes = list(csv.reader(io.StringIO(contenu), delimiter=";"))[1:]
    assert len(lignes) == n, f"{len(lignes)} ligne(s) au lieu de {n}"


@then("la réponse est un JSON de {n:d} saisies")
def etape_json(context, n):
    donnees = context.reponse.get_json()
    assert isinstance(donnees, list) and len(donnees) == n


@then('la première saisie concerne l\'opérateur "{operateur}"')
def etape_json_operateur(context, operateur):
    assert context.reponse.get_json()[0]["operateur"] == operateur


# ---------- Sécurité et mode démo ----------

@given("l'application est en mode démo")
def etape_mode_demo(context):
    from app import app
    app.config["DEMO"] = True
    context.autre_client = app.test_client()


@when('un premier visiteur déclare une sortie de 5 pièces "{piece}"')
def etape_visiteur1(context, piece):
    context.reponse = context.client.post("/", data={"operateur": "Visiteur 1", "piece": piece, "quantite": "5"})


@then('un second visiteur ne voit pas la pièce "{piece}"')
def etape_visiteur2(context, piece):
    assert piece not in context.autre_client.get("/").get_data(as_text=True)


@then('le premier visiteur voit la pièce "{piece}"')
def etape_visiteur1_voit(context, piece):
    assert piece in context.client.get("/").get_data(as_text=True)


@when("un visiteur enregistre {n:d} saisies")
def etape_n_saisies(context, n):
    for i in range(n):
        context.reponse = context.client.post("/", data={"operateur": "V", "piece": f"P{i}", "quantite": "1"})


@then('la dernière saisie est refusée avec le message "{message}"')
def etape_derniere_refusee(context, message):
    assert context.reponse.status_code == 400
    assert message in context.reponse.get_data(as_text=True)


@when("je déclare une sortie avec un opérateur de {n:d} caractères")
def etape_operateur_long(context, n):
    context.reponse = context.client.post("/", data={"operateur": "A" * n, "piece": "X", "quantite": "1"})


@then('la cellule exportée vaut "{valeur}"')
def etape_cellule(context, valeur):
    contenu = context.reponse.get_data(as_text=True).lstrip("﻿")
    cellules = [c for ligne in csv.reader(io.StringIO(contenu), delimiter=";") for c in ligne]
    assert valeur in cellules, cellules


@then('la réponse contient l\'en-tête de sécurité "{entete}"')
def etape_entete_securite(context, entete):
    assert entete in context.reponse.headers, dict(context.reponse.headers)
