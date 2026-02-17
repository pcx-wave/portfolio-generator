# Guide d'Utilisation de l'Éditeur Manuel

## Introduction

L'éditeur manuel (`manual_editor.html`) est une interface web interactive qui vous permet de créer et éditer manuellement tous les champs de votre portfolio avant de le générer.

## Comment l'utiliser

### 1. Ouvrir l'éditeur

Ouvrez le fichier `manual_editor.html` dans votre navigateur web :

```bash
# Option 1 : Ouvrir directement le fichier
open manual_editor.html  # macOS
xdg-open manual_editor.html  # Linux
start manual_editor.html  # Windows

# Option 2 : Via un serveur web local
python -m http.server 8080
# Puis ouvrez http://localhost:8080/manual_editor.html dans votre navigateur
```

### 2. Remplir le formulaire

#### Informations de base (obligatoires)
- **Nom complet** : Votre nom et prénom
- **Titre/Fonction** : Votre titre professionnel (ex: Développeur Full-Stack)
- **Biographie** : Une courte présentation de votre parcours
- **Photo de profil** : URL d'une image (optionnel)

#### Informations de contact
- Email
- Téléphone
- Adresse complète

#### Profils sociaux
Cliquez sur "+ Ajouter un profil" pour ajouter vos profils sociaux :
- LinkedIn
- GitHub
- Twitter
- Portfolio personnel
- etc.

#### Compétences
Cliquez sur "+ Ajouter une compétence" pour lister vos compétences techniques et soft skills :
- Langages de programmation
- Frameworks
- Outils
- Compétences métier

#### Formation
Cliquez sur "+ Ajouter une formation" pour ajouter vos diplômes et formations :
- Établissement
- Type de diplôme (Licence, Master, etc.)
- Domaine d'études
- Dates de début et fin
- Note ou mention obtenue

#### Projets & Réalisations
Cliquez sur "+ Ajouter un projet" pour présenter vos projets :
- Titre du projet
- Description détaillée
- URL d'une image (optionnel)

### 3. Configuration du site

Choisissez le type de site et le thème de design :

**Types de site :**
- **Hybride** : Affiche à la fois vos projets et votre CV
- **Portfolio** : Affiche uniquement vos projets
- **CV** : Affiche uniquement vos expériences professionnelles

**Thèmes de design :**
- **Classique** : Style neutre et professionnel
- **Moderne** : Design avec dégradés et effets modernes
- **Contraste** : Noir/blanc/jaune pour une lisibilité optimale
- **Artistique** : Style créatif avec formes organiques

### 4. Générer le JSON

Une fois tous les champs remplis, cliquez sur "✓ Générer le JSON".

Le JSON généré s'affichera en bas de la page avec deux options :
- **📋 Copier le JSON** : Copie le JSON dans le presse-papier
- **💾 Télécharger le JSON** : Télécharge le fichier JSON

### 5. Utiliser le JSON généré

#### Via la ligne de commande

```bash
python generate_portfolio.py \
  --input portfolio_data.json \
  --output-dir dist/mon-portfolio \
  --site-template hybrid \
  --design-theme modern
```

#### Via Python

```python
import json
from generate_portfolio import generate_portfolio

# Charger le JSON généré
with open('portfolio_data.json', 'r') as f:
    user_data = json.load(f)

# Générer le portfolio
result = generate_portfolio(
    user_data,
    output_dir="dist/mon-portfolio",
    site_template="hybrid",
    design_theme="modern"
)

print(f"Portfolio généré dans : {result['path']}")
print(f"URL de l'éditeur CMS : {result['admin_url']}")
```

## Fonctionnalités supplémentaires

### Charger un exemple

Cliquez sur "📋 Charger un exemple" pour pré-remplir le formulaire avec des données d'exemple. Cela vous permet de :
- Voir comment utiliser l'éditeur
- Avoir un point de départ pour votre propre portfolio
- Tester rapidement le générateur

### Réinitialiser le formulaire

Cliquez sur "🗑️ Réinitialiser" pour effacer tous les champs et recommencer à zéro.

### Ajouter/Supprimer des éléments dynamiquement

Vous pouvez :
- Ajouter autant de profils, compétences, formations et projets que nécessaire
- Supprimer un élément en cliquant sur le bouton "✕" en haut à droite de chaque élément

## Format du JSON généré

L'éditeur génère un JSON au format JSON Resume compatible avec le générateur de portfolio :

```json
{
  "basics": {
    "name": "Votre Nom",
    "summary": "Votre bio",
    "label": "Votre titre",
    "image": "URL de votre photo",
    "email": "votre@email.com",
    "phone": "+33 6 00 00 00 00",
    "location": {
      "address": "Votre adresse"
    },
    "profiles": [
      {
        "network": "LinkedIn",
        "url": "https://linkedin.com/in/vous"
      }
    ]
  },
  "skills": [
    {"name": "JavaScript"},
    {"name": "Python"}
  ],
  "education": [
    {
      "institution": "Université",
      "studyType": "Master",
      "area": "Informatique",
      "startDate": "2020",
      "endDate": "2022"
    }
  ],
  "projects": [
    {
      "name": "Mon Projet",
      "description": "Description du projet",
      "image": "URL de l'image"
    }
  ]
}
```

## Workflow complet

```
┌─────────────────────────────────┐
│  1. Ouvrir manual_editor.html   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  2. Remplir tous les champs     │
│     (nom, bio, projets, etc.)   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  3. Générer et télécharger JSON │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  4. Utiliser le JSON avec       │
│     generate_portfolio.py       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  5. Portfolio statique généré   │
│     prêt pour déploiement       │
└─────────────────────────────────┘
```

## Questions fréquentes

**Q : Les champs sont-ils tous obligatoires ?**  
R : Non, seuls le nom et la bio sont obligatoires. Tous les autres champs sont optionnels.

**Q : Puis-je modifier le JSON après l'avoir généré ?**  
R : Oui, vous pouvez éditer le fichier JSON avec n'importe quel éditeur de texte.

**Q : Puis-je réutiliser un JSON existant ?**  
R : Oui, mais l'éditeur ne permet pas encore de charger un JSON existant pour le modifier. Vous devrez soit éditer le JSON manuellement, soit recréer les données dans l'éditeur.

**Q : Que faire si je veux éditer mon portfolio après génération ?**  
R : Après la génération, vous pouvez utiliser Decap CMS en accédant à `/admin/` dans votre portfolio généré.

## Support

Pour toute question ou problème, consultez le fichier `README.md` du projet ou créez une issue sur GitHub.
