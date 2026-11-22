# Captation de données atelier (Flask)

**Démo en ligne :**

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
| Plan de test et bilan de campagne (18 scénarios) | [docs/plan-de-test.md](docs/plan-de-test.md) |
| Rapports d'anomalie : saisies invalides (ANO-001) et injection de formules CSV (ANO-002), corrigées | [docs/rapport-anomalie.md](docs/rapport-anomalie.md) |

```bash
behave --lang fr   # 18 scénarios, 66 étapes
```

## Sécurité de la démo en ligne

| Risque | Protection |
|---|---|
| Un visiteur modifie ce que voient les autres | Mode démo : les saisies de chaque visiteur restent dans sa session (cookie signé) |
| Spam, textes géants | 40 caractères max par champ, 20 saisies max par visiteur, requêtes de 16 Ko max |
| Injection de code HTML / JavaScript | Échappement automatique des templates + Content-Security-Policy sans script |
| Injection de formules dans l'export Excel | Neutralisation des cellules commençant par `=`, `+`, `-`, `@` (ANO-002) |
| Affichage de la page dans un cadre (clickjacking) | `X-Frame-Options: DENY` et `frame-ancestors 'none'` |
| Console de debug exposée | Debug uniquement en local ; en ligne, l'appli tourne avec gunicorn |
| Clé secrète dans le code | Générée par l'hébergeur et lue dans une variable d'environnement |

## Déploiement (Render)
Le fichier `render.yaml` configure tout : `DEMO_MODE=1`, clé secrète générée automatiquement,
lancement avec `gunicorn app:app`.
