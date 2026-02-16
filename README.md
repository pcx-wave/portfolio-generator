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

## Utilisation
1. Remplace `TON_GITHUB_TOKEN` et `TON_NETLIFY_TOKEN` dans `generate_portfolio.py`.
2. Exécute le script avec tes données utilisateur :
```python
user_data = {
    "name": "Nom Utilisateur",
    "bio": "Bio de l'utilisateur",
    "projects": [
        {"title": "Projet 1", "description": "Description", "image": "image.jpg"}
    ]
}
generate_portfolio(user_data)
```

## Intégration avec JobsMatch
- Utilise le formulaire `form_example.html` pour collecter les données.
- Appelle le script via une API ou un backend.

## Structure
- `templates/` : Templates HTML/CSS
- `generate_portfolio.py` : Script principal
- `form_example.html` : Exemple de formulaire

## Déploiement
Chaque portfolio est déployé sur Netlify avec Decap CMS pour l'édition.

## Licence
MIT