# Captation de données atelier (Flask)

Mini-outil web pour déclarer les sorties de pièces en atelier, pensé pour des utilisateurs non informaticiens.

![Aperçu](capture.png)

## Fonctionnalités
- **Saisie** rapide via un formulaire (opérateur, référence pièce, quantité), enregistrée en CSV
- **Recherche / filtre** par opérateur ou par pièce
- **Export CSV** compatible Excel (et réutilisable dans un outil d'analyse type Dataiku)
- **API JSON** : `GET /api/saisies?q=...`
- **Validation côté serveur** des saisies (champs obligatoires, quantité entière ≥ 1)
- **Rapport automatique** : `rapport.py` interroge l'API en HTTP et génère un récapitulatif (totaux par pièce et par opérateur) ; `rapport.bat` l'automatise et archive les rapports sous Windows

**Stack :** Python · Flask · Jinja2 · HTML/CSS · API REST · Batch

## Lancer le projet
```bash
pip install -r requirements.txt
python3 app.py          # puis ouvrir http://127.0.0.1:5000
python3 rapport.py      # dans un autre terminal, génère le rapport
```

## Démarche Business Analyst & tests (BDD)

J'ai appliqué à cet outil la démarche d'une Business Analyst : du besoin aux tests automatisés.

| Étape | Document |
|---|---|
| Expression du besoin, personas, 4 user stories et critères d'acceptation | [docs/user-stories.md](docs/user-stories.md) |
| Scénarios Gherkin (français) automatisés avec `behave` (équivalent Python de Cucumber) | [features/](features/) |
| Plan de test et bilan de campagne (13 scénarios) | [docs/plan-de-test.md](docs/plan-de-test.md) |
| Rapport d'anomalie : saisies invalides acceptées par le serveur, puis corrigées | [docs/rapport-anomalie.md](docs/rapport-anomalie.md) |

```bash
behave --lang fr   # 13 scénarios, 49 étapes
```
