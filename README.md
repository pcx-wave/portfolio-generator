# Portfolio Generator

Ce dépôt contient un script Python pour générer des portfolios statiques avec intégration Decap CMS et déploiement automatique sur Netlify. **Nouveau:** Support complet pour Astro CMS!

## 🎯 Deux Modes de Génération

1. **Static HTML** (par défaut) - Site HTML/CSS traditionnel avec Decap CMS
2. **Astro** (nouveau!) - Projet Astro moderne avec environnement de développement complet

## Prérequis
- Python 3.8+
- MongoDB (optionnel, si vous voulez persister les portfolios)
- Node.js (pour projets Astro)

## Installation
```bash
pip install flask flask-cors
```

## 🚀 Génération Astro (Nouveau!)

**Générer un projet Astro moderne:**

```bash
# Via CLI
python generate_portfolio.py --input user_data.json --output-dir my-portfolio --astro

# Avec template et thème
python generate_portfolio.py \
  --input user_data.json \
  --output-dir my-portfolio \
  --astro \
  --site-template hybrid \
  --design-theme modern
```

**Le projet Astro généré inclut:**
- ✅ Structure de projet Astro complète
- ✅ Hot reload pour développement
- ✅ Support TypeScript
- ✅ Build optimisé
- ✅ Toutes vos données en JSON
- ✅ Components .astro personnalisables

**Utiliser le projet Astro:**
```bash
cd my-portfolio
npm install
npm run dev  # Ouvre http://localhost:4321
```

📚 **Documentation complète:** [ASTRO_COMPATIBILITY_GUIDE.md](ASTRO_COMPATIBILITY_GUIDE.md)

## Édition Manuelle des Champs

**Nouveau !** Vous pouvez maintenant éditer manuellement tous les champs avant génération via l'interface web :

1. Ouvrez `manual_editor.html` dans votre navigateur
2. Remplissez tous les champs (nom, bio, projets, compétences, formation, etc.)
3. Ajoutez/supprimez dynamiquement des projets, compétences, formations et profils sociaux
4. Cliquez sur "Générer le JSON" pour créer votre fichier de données
5. Copiez ou téléchargez le JSON généré
6. Utilisez ce JSON avec le générateur de portfolio

L'éditeur manuel permet de :
- ✓ Éditer tous les champs de manière interactive
- ✓ Ajouter/supprimer des projets, compétences, formations
- ✓ Prévisualiser le JSON avant génération
- ✓ Copier ou télécharger le JSON
- ✓ Charger un exemple pré-rempli pour démarrer rapidement

## Utilisation (module appelable par un autre service)
Le module expose `generate_portfolio(user_data, output_dir="dist", site_template="hybrid", design_theme="classic")` pour être appelé directement par votre service de matching.

### Workflow cible (JSON Resume -> template -> draft -> édition -> validation -> déploiement)

Oui, le process est bien celui-ci :
1. **Édition manuelle AVANT génération** (nouveau!) via `manual_editor.html` OU réception de données JSON Resume (ou format simple legacy)
2. Sélection du template de site (`portfolio`, `cv`, `hybrid`)
3. Sélection du design (`classic`, `modern`, `contrast`, `artistic`)
4. Génération d'un **draft** statique
5. **Édition manuelle APRÈS génération** via Decap CMS (`/admin`)
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

## Intégration avec JobsMatch et Édition à Distance

### Mode 1: API REST (Recommandé pour JobsMatch)

Le générateur propose maintenant une **API REST complète** pour l'intégration avec des plateformes externes.

**Démarrer le serveur API:**
```bash
pip install flask flask-cors
python api_server.py
```

**Endpoints disponibles:**
- `POST /api/generate` - Créer un portfolio depuis JobsMatch
- `GET /api/portfolio/<id>` - Récupérer les données du portfolio
- `PUT /api/portfolio/<id>` - Mettre à jour un portfolio
- `GET /editor` - Éditeur manuel accessible à distance
- `GET /editor/<id>` - Éditeur pré-rempli avec données existantes

**Exemple d'intégration Python (pour JobsMatch):**
```python
import requests

# Créer un portfolio pour un utilisateur JobsMatch
response = requests.post('http://api.example.com/api/generate', json={
    "user_id": "jobsmatch-user-123",
    "basics": {
        "name": "Alice Dupont",
        "summary": "Développeuse Full-Stack",
        "email": "alice@jobsmatch.com"
    },
    "projects": [...],
    "skills": [...],
    "site_template": "hybrid",
    "design_theme": "modern"
})

result = response.json()
portfolio_url = result['portfolio_url']
editor_url = result['editor_url']  # URL pour que l'utilisateur édite son portfolio
```

**Intégration iframe (pour édition dans JobsMatch):**
```html
<!-- Dans la page de profil JobsMatch -->
<iframe 
    src="http://api.example.com/editor/{portfolio_id}"
    width="100%" 
    height="800px">
</iframe>
```

**Voir la documentation complète:**
- [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) - Documentation complète de l'API
- [`jobsmatch_integration_example.py`](jobsmatch_integration_example.py) - Exemples d'intégration

### Mode 2: Éditeur Manuel avec Paramètres URL

L'éditeur manuel supporte maintenant le pré-remplissage via URL:

```
http://localhost:8080/manual_editor.html?name=Alice&bio=Développeuse&email=alice@example.com
```

Ou avec JSON complet:
```javascript
const data = {basics: {name: "Alice", summary: "Bio"}};
const url = `editor.html?data=${encodeURIComponent(JSON.stringify(data))}`;
```

### Mode 3: Communication PostMessage (pour iframes)

L'éditeur supporte la communication bidirectionnelle avec des applications parentes:

```javascript
// Dans JobsMatch (fenêtre parente)
const editor = document.getElementById('portfolio-editor-frame');

// Écouter les événements de l'éditeur
window.addEventListener('message', function(event) {
    if (event.data.type === 'portfolio-generated') {
        console.log('Portfolio créé:', event.data.data);
        // Sauvegarder dans JobsMatch
        saveToJobsMatch(event.data.data);
    }
});

// Pré-remplir l'éditeur
editor.contentWindow.postMessage({
    type: 'prefill-data',
    data: userDataFromJobsMatch
}, '*');
```

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
