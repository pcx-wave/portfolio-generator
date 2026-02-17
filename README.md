# Portfolio Generator

Ce dépôt contient un script Python pour générer des portfolios statiques avec intégration Decap CMS et déploiement automatique sur Netlify.

## Prérequis
- Python 3.8+
- Un token GitHub (pour créer des dépôts)
- Un token Netlify (pour déployer)

## Installation
```bash
pip install requests pyyaml
```

## Utilisation (module appelable par un autre service)
Le module expose `generate_portfolio(user_data, output_dir="dist")` pour être appelé directement par votre service de matching.

### Comment le générateur fonctionne (input -> output)

#### 1) Input attendu
Le générateur attend un objet JSON (ou dict Python) avec cette structure :

```json
{
  "name": "Nom Utilisateur",
  "bio": "Bio de l'utilisateur",
  "projects": [
    {
      "title": "Projet 1",
      "description": "Description du projet",
      "image": "https://example.com/image.jpg"
    }
  ]
}
```

- `name` : requis
- `bio` : requis
- `projects` : liste (peut être vide)
- `projects[].image` : optionnel (une image par défaut est utilisée si vide)

#### 2) Ce qui se passe pendant la génération
- Le template `templates/index.html` est rempli avec vos données.
- Le CSS `templates/styles/main.css` est copié.
- Les fichiers Decap CMS sont créés (`admin/index.html`, `admin/config.yml`).
- Les données éditables sont écrites dans `data/portfolio.json`.
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
  netlify.toml
```

La fonction retourne :

```json
{
  "path": "/chemin/absolu/vers/dist/user-123",
  "admin_url": "/admin/"
}
```

```python
from generate_portfolio import generate_portfolio

user_data = {
    "name": "Nom Utilisateur",
    "bio": "Bio de l'utilisateur",
    "projects": [
        {"title": "Projet 1", "description": "Description", "image": "image.jpg"}
    ]
}
result = generate_portfolio(user_data, output_dir="dist/user-123")
print(result)
```

Ou via CLI (utile pour intégration backend/worker) :
```bash
python generate_portfolio.py --input user_data.json --output-dir dist/user-123
```

## Intégration avec JobsMatch
- Utilise le formulaire `form_example.html` pour collecter les données.
- Appelle le script via une API ou un backend.

## Structure
- `templates/` : Templates HTML/CSS
- `generate_portfolio.py` : Script principal
- `form_example.html` : Exemple de formulaire

## Déploiement Netlify + édition utilisateur
Le site généré contient automatiquement :
- `admin/index.html` et `admin/config.yml` (Decap CMS)
- `data/portfolio.json` (contenu éditable)
- `netlify.toml` (publication statique)

Vous pouvez donc déployer le dossier généré directement sur Netlify, puis laisser l'utilisateur éditer son portfolio via `/admin`.

## Option CMS Jamstack
- **Par défaut : Decap CMS** (léger, Git-friendly, simple sur Netlify)
- **Alternative possible : TinaCMS** si vous préférez une édition plus orientée React

## Licence
MIT
