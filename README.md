# Portfolio Generator

Ce dépôt contient un script Python pour générer des portfolios statiques avec intégration Decap CMS et déploiement automatique sur Netlify.

## Prérequis
- Python 3.8+
- MongoDB (optionnel, si vous voulez persister les portfolios)

## Installation
```bash
pip install requests pyyaml
```

## Utilisation (module appelable par un autre service)
Le module expose `generate_portfolio(user_data, output_dir="dist", site_template="hybrid", design_theme="classic")` pour être appelé directement par votre service de matching.

### Workflow cible (JSON Resume -> template -> draft -> édition -> validation -> déploiement)

Oui, le process est bien celui-ci :
1. Réception de données JSON Resume (ou format simple legacy)
2. Sélection du template de site (`portfolio`, `cv`, `hybrid`)
3. Sélection du design (`classic`, `modern`, `contrast`, `artistic`)
4. Génération d'un **draft** statique
5. Édition manuelle éventuelle via Decap CMS (`/admin`)
6. Validation explicite du draft
7. Déploiement (Netlify-ready)

### Comment le générateur fonctionne (input -> output, architecture NoSQL)

#### 1) Input attendu
Le générateur supporte **2 formats d'entrée** :

- **Format portfolio simple (historique)** : `templates/input_template_legacy.json`
- **Format CV augmenté (JSON Resume-like)** : `templates/input_template_cv_augmente.json`
- **Format JSON Resume complet (démo placeholders)** : `templates/input_template_jsonresume_full.json`

Format portfolio simple :

```json
{
  "name": "Nom Utilisateur",
  "bio": "Bio de l'utilisateur",
  "user_id": "user-123",
  "projects": [
    {
      "title": "Projet 1",
      "description": "Description du projet",
      "image": "https://example.com/image.jpg"
    }
  ]
}
```

Format CV augmenté (proche JSON Resume) :
```json
{
  "user_id": "user-123",
  "basics": {
    "name": "Nom Utilisateur",
    "summary": "Résumé professionnel"
  },
  "work": [
    {
      "name": "Entreprise",
      "position": "Poste",
      "summary": "Contexte",
      "highlights": ["Impact 1", "Impact 2"]
    }
  ],
  "projects": [
    {
      "name": "Projet",
      "description": "Description",
      "image": "https://example.com/project.png"
    }
  ]
}
```

- `name`/`bio` : requis pour le format portfolio simple
- `basics.name` + `basics.summary` (ou `basics.label`) : requis pour le format CV augmenté
- `user_id` : optionnel (généré automatiquement si absent ou vide)
- `projects` : liste (peut être vide)
- `projects[].image` : optionnel (une image par défaut est utilisée si vide)

#### 2) Ce qui se passe pendant la génération
- Si l'entrée est en format CV augmenté, elle est convertie automatiquement en format portfolio (`name`, `bio`, `projects`).
- Un document canonique NoSQL est construit (`portfolio_id`, `user_id`, `created_at`, `updated_at`, `projects[].project_id`).
- Le template `templates/index.html` est rempli avec vos données.
- Le CSS `templates/styles/main.css` est copié.
- Les fichiers Decap CMS sont créés (`admin/index.html`, `admin/config.yml`).
- Les données éditables sont écrites dans `data/portfolio.json`.
- Le document NoSQL est écrit dans `data/portfolio_document.json`.
- Une projection SQL-friendly (tables `portfolios` + `projects`) est écrite dans `data/portfolio_sql_projection.json`.
- L'état du workflow est écrit dans `data/workflow_state.json` (draft/validated).
- La config Netlify `netlify.toml` est créée.

#### 3) Output généré
Dans le dossier `output_dir` (ex: `dist/user-123`), vous obtenez :

```text
dist/user-123/
  index.html
  styles/main.css
  admin/index.html
  admin/config.yml
  data/portfolio.json
  data/portfolio_document.json
  data/portfolio_sql_projection.json
  data/workflow_state.json
  netlify.toml
```

La fonction retourne :

```json
{
  "path": "/chemin/absolu/vers/dist/user-123",
  "admin_url": "/admin/",
  "portfolio_id": "uuid"
}
```

```python
from generate_portfolio import generate_portfolio

user_data = {
    "name": "Nom Utilisateur",
    "bio": "Bio de l'utilisateur",
    "user_id": "user-123",
    "projects": [
        {"title": "Projet 1", "description": "Description", "image": "image.jpg"}
    ]
}
result = generate_portfolio(user_data, output_dir="dist/user-123", site_template="hybrid", design_theme="modern")
print(result)
```

Avec MongoDB (optionnel) :
```python
from pymongo import MongoClient
from generate_portfolio import generate_portfolio

collection = MongoClient()["portfolio_db"]["portfolios"]
result = generate_portfolio(
    user_data,
    output_dir="dist/user-123",
    mongo_collection=collection,
    site_template="hybrid",
    design_theme="modern"
)
```

Ou via CLI (utile pour intégration backend/worker) :
```bash
python generate_portfolio.py --input user_data.json --site-template hybrid --design-theme artistic --output-dir dist/user-123
```

Validation d'un draft généré :
```bash
python generate_portfolio.py --validate --output-dir dist/user-123
```

## Intégration avec JobsMatch
- Utilise le formulaire `form_example.html` pour collecter les données.
- Appelle le script via une API ou un backend.

## Structure
- `templates/` : Templates HTML/CSS
- `templates/input_template_legacy.json` : Exemple format simple
- `templates/input_template_cv_augmente.json` : Exemple format CV augmenté
- `templates/input_template_jsonresume_full.json` : Exemple JSON Resume complet (photo, adresse, éducation, skills, profils)
- `generate_portfolio.py` : Script principal
- `form_example.html` : Exemple de formulaire

## Références templates CV standards
- JSON Resume (schema open-source largement utilisé) : https://jsonresume.org/schema/
- Documentation JSON Resume : https://docs.jsonresume.org/

## Déploiement Netlify + édition utilisateur
Le site généré contient automatiquement :
- `admin/index.html` et `admin/config.yml` (Decap CMS)
- `data/portfolio.json` (contenu éditable)
- `netlify.toml` (publication statique)

Vous pouvez donc déployer le dossier généré directement sur Netlify, puis laisser l'utilisateur éditer son portfolio via `/admin`.

## Option CMS Jamstack
- **Par défaut : Decap CMS** (léger, Git-friendly, simple sur Netlify)
- **Alternative possible : TinaCMS** si vous préférez une édition plus orientée React

## Designs proposés à l'utilisateur
- `classic` : style actuel, neutre et polyvalent
- `modern` : dégradés, cartes arrondies, rendu plus startup/product
- `contrast` : noir/blanc/jaune, lisibilité forte (accessible)
- `artistic` : rendu plus créatif (formes organiques, dégradés, ambiance éditoriale)

## Licence
MIT
