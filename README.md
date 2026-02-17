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
