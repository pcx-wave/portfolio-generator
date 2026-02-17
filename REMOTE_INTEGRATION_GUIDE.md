# Guide d'Intégration à Distance - Portfolio Generator

## Vue d'ensemble

Ce guide explique comment intégrer le Portfolio Generator avec des plateformes externes comme JobsMatch pour permettre aux utilisateurs de créer et éditer leurs portfolios à distance.

## Problématique

**Question:** "Can this editor be used remotely? How can someone registered on JobsMatch (another repo/website) edit their page created by calling this generator?"

**Réponse:** OUI! Le Portfolio Generator propose maintenant **trois modes d'intégration à distance**.

## 🌐 Mode 1: API REST (Recommandé)

### Avantages
- ✓ Intégration programmatique complète
- ✓ Création/mise à jour/lecture de portfolios via HTTP
- ✓ Serveur dédié pour gérer les portfolios
- ✓ Support CORS pour intégrations cross-origin
- ✓ Édition via endpoints API

### Mise en place

1. **Installation des dépendances:**
```bash
pip install flask flask-cors
```

2. **Démarrage du serveur:**
```bash
python api_server.py
# Serveur démarré sur http://localhost:5000
```

3. **Variables d'environnement:**
```bash
export PORT=5000
export DEBUG=false
export PORTFOLIOS_DIR=generated_portfolios
```

### Intégration avec JobsMatch

#### Scénario 1: Créer un Portfolio Automatiquement

Lorsqu'un utilisateur s'inscrit sur JobsMatch:

```python
import requests

def create_portfolio_for_jobsmatch_user(user_data):
    """Créer un portfolio pour un nouvel utilisateur JobsMatch."""
    
    api_url = "https://portfolio-api.example.com"
    
    portfolio_request = {
        "user_id": user_data['id'],
        "basics": {
            "name": user_data['full_name'],
            "summary": user_data['bio'],
            "email": user_data['email'],
            "label": user_data.get('job_title', ''),
            "profiles": [
                {"network": profile['platform'], "url": profile['url']}
                for profile in user_data.get('social_profiles', [])
            ]
        },
        "skills": [{"name": skill} for skill in user_data.get('skills', [])],
        "projects": user_data.get('projects', []),
        "site_template": "hybrid",
        "design_theme": "modern"
    }
    
    response = requests.post(
        f"{api_url}/api/generate",
        json=portfolio_request
    )
    
    if response.status_code == 201:
        result = response.json()
        
        # Sauvegarder les URLs dans la DB JobsMatch
        save_to_jobsmatch_db(
            user_id=user_data['id'],
            portfolio_id=result['portfolio_id'],
            portfolio_url=result['portfolio_url'],
            editor_url=result['editor_url']
        )
        
        return result
    else:
        raise Exception(f"Portfolio creation failed: {response.text}")
```

#### Scénario 2: Mettre à Jour Automatiquement

Lorsqu'un utilisateur met à jour son profil JobsMatch:

```python
def sync_profile_to_portfolio(user_id, updated_data):
    """Synchroniser le profil JobsMatch avec le portfolio."""
    
    portfolio_id = get_portfolio_id_from_db(user_id)
    
    response = requests.put(
        f"https://portfolio-api.example.com/api/portfolio/{portfolio_id}",
        json={
            "name": updated_data.get('full_name'),
            "bio": updated_data.get('bio'),
            "headline": updated_data.get('job_title'),
            "regenerate": True  # Regénérer le HTML
        }
    )
    
    return response.json()
```

#### Scénario 3: Intégrer l'Éditeur dans JobsMatch

##### Option A: Iframe (Simple)

```html
<!-- Dans la page de profil JobsMatch -->
<div class="portfolio-section">
    <h2>Mon Portfolio</h2>
    <p>Personnalisez votre portfolio pour vous démarquer auprès des employeurs.</p>
    
    <div class="portfolio-editor-container">
        <iframe 
            id="portfolio-editor"
            src="https://portfolio-api.example.com/editor/{{ user.portfolio_id }}"
            width="100%" 
            height="800px"
            style="border: 1px solid #ddd; border-radius: 8px;">
        </iframe>
    </div>
</div>

<script>
    // Écouter les événements de l'éditeur
    window.addEventListener('message', function(event) {
        if (event.origin !== "https://portfolio-api.example.com") return;
        
        if (event.data.type === 'portfolio-generated') {
            // Portfolio sauvegardé, notifier l'utilisateur
            showSuccessMessage('✓ Portfolio sauvegardé avec succès !');
            
            // Optionnel: envoyer au backend JobsMatch
            fetch('/api/portfolio/saved', {
                method: 'POST',
                body: JSON.stringify({
                    portfolio_data: event.data.data
                })
            });
        }
    });
</script>
```

##### Option B: Lien Direct

```html
<!-- Bouton pour ouvrir l'éditeur dans un nouvel onglet -->
<a href="https://portfolio-api.example.com/editor/{{ user.portfolio_id }}" 
   target="_blank" 
   class="btn btn-primary">
    ✏️ Éditer mon portfolio
</a>
```

##### Option C: Communication Bidirectionnelle

```javascript
// Dans JobsMatch - Pré-remplir l'éditeur avec les données utilisateur
const editorFrame = document.getElementById('portfolio-editor');

editorFrame.onload = function() {
    // Envoyer les données à l'éditeur
    editorFrame.contentWindow.postMessage({
        type: 'prefill-data',
        data: {
            basics: {
                name: userData.full_name,
                summary: userData.bio,
                email: userData.email
            },
            projects: userData.projects,
            skills: userData.skills
        }
    }, 'https://portfolio-api.example.com');
};

// Écouter les données de retour
window.addEventListener('message', function(event) {
    if (event.data.type === 'get-data') {
        // L'éditeur demande les données
        event.source.postMessage({
            type: 'form-data',
            data: currentUserData
        }, event.origin);
    }
});
```

## 🔗 Mode 2: URL Parameters

### Avantages
- ✓ Simple et rapide
- ✓ Pas de backend nécessaire
- ✓ Fonctionne avec l'éditeur statique

### Utilisation

#### Pré-remplir des champs simples:

```
https://example.com/manual_editor.html?name=John+Doe&bio=Developer&email=john@example.com
```

#### Pré-remplir avec JSON complet:

```javascript
// Dans JobsMatch
const portfolioData = {
    basics: {
        name: user.full_name,
        summary: user.bio,
        email: user.email
    },
    projects: user.projects,
    skills: user.skills
};

const editorUrl = 
    `https://example.com/manual_editor.html?data=${encodeURIComponent(JSON.stringify(portfolioData))}`;

// Rediriger l'utilisateur
window.location.href = editorUrl;

// Ou ouvrir dans nouvel onglet
window.open(editorUrl, '_blank');
```

## 📨 Mode 3: PostMessage API

### Avantages
- ✓ Communication bidirectionnelle
- ✓ Sécurisé avec validation d'origine
- ✓ Idéal pour intégration iframe

### Implémentation Complète

```javascript
// Dans JobsMatch (application parente)
class PortfolioEditorIntegration {
    constructor(iframeId, editorOrigin) {
        this.iframe = document.getElementById(iframeId);
        this.editorOrigin = editorOrigin;
        this.setupListeners();
    }
    
    setupListeners() {
        window.addEventListener('message', (event) => {
            // Validation de sécurité
            if (event.origin !== this.editorOrigin) return;
            
            this.handleMessage(event.data);
        });
    }
    
    handleMessage(data) {
        switch(data.type) {
            case 'portfolio-generated':
                this.onPortfolioGenerated(data.data);
                break;
            case 'editor-ready':
                this.onEditorReady();
                break;
            case 'form-data':
                this.onFormDataReceived(data.data);
                break;
        }
    }
    
    onPortfolioGenerated(portfolioData) {
        console.log('Portfolio créé:', portfolioData);
        
        // Sauvegarder dans JobsMatch
        fetch('/api/save-portfolio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: currentUserId,
                portfolio: portfolioData
            })
        });
        
        // Notifier l'utilisateur
        showNotification('✓ Portfolio sauvegardé avec succès !');
    }
    
    onEditorReady() {
        // L'éditeur est prêt, envoyer les données
        this.prefillEditor(currentUserData);
    }
    
    prefillEditor(userData) {
        this.sendMessage({
            type: 'prefill-data',
            data: {
                basics: {
                    name: userData.full_name,
                    summary: userData.bio,
                    email: userData.email,
                    profiles: userData.social_profiles
                },
                skills: userData.skills,
                projects: userData.projects,
                education: userData.education
            }
        });
    }
    
    sendMessage(data) {
        this.iframe.contentWindow.postMessage(data, this.editorOrigin);
    }
    
    requestCurrentData() {
        this.sendMessage({ type: 'get-data' });
    }
}

// Utilisation
const editor = new PortfolioEditorIntegration(
    'portfolio-editor',
    'https://portfolio-api.example.com'
);

// Demander les données actuelles de l'éditeur
document.getElementById('save-btn').addEventListener('click', () => {
    editor.requestCurrentData();
});
```

## 🚀 Déploiement en Production

### Option 1: Serveur dédié

```bash
# Avec Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Option 2: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

```bash
docker build -t portfolio-api .
docker run -p 5000:5000 -v $(pwd)/generated_portfolios:/app/generated_portfolios portfolio-api
```

### Option 3: Platform-as-a-Service

**Heroku:**
```bash
# Créer Procfile
echo "web: gunicorn api_server:app" > Procfile

# Déployer
git push heroku main
```

**Railway / Render:**
- Connecter le repo GitHub
- Définir la commande: `gunicorn api_server:app`
- Définir PORT dans les variables d'environnement

## 🔒 Sécurité

### 1. Authentification

Ajouter l'authentification par API key:

```python
# Dans api_server.py
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/generate", methods=["POST"])
@require_api_key
def api_generate_portfolio():
    # ...
```

### 2. CORS Restreint

```python
from flask_cors import CORS

CORS(app, origins=["https://jobsmatch.com"])
```

### 3. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/api/generate", methods=["POST"])
@limiter.limit("10 per minute")
def api_generate_portfolio():
    # ...
```

### 4. Validation d'Origine PostMessage

```javascript
// Toujours valider l'origine
window.addEventListener('message', function(event) {
    // Liste blanche des origines autorisées
    const allowedOrigins = [
        'https://portfolio-api.example.com',
        'https://jobsmatch.com'
    ];
    
    if (!allowedOrigins.includes(event.origin)) {
        console.warn('Message ignoré de:', event.origin);
        return;
    }
    
    // Traiter le message
    handleMessage(event.data);
});
```

## 📊 Monitoring

### Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/api/generate", methods=["POST"])
def api_generate_portfolio():
    logger.info(f"Portfolio generation requested by {request.remote_addr}")
    # ...
```

### Métriques

```python
from prometheus_client import Counter, Histogram

portfolios_created = Counter('portfolios_created_total', 'Total portfolios created')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.route("/api/generate", methods=["POST"])
def api_generate_portfolio():
    with request_duration.time():
        result = generate_portfolio(...)
        portfolios_created.inc()
        return result
```

## 🎯 Cas d'Usage Complets

### Exemple 1: JobsMatch avec Django

```python
# jobsmatch/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests

@login_required
def portfolio_page(request):
    user = request.user
    portfolio_api = "https://portfolio-api.example.com"
    
    # Créer le portfolio s'il n'existe pas
    if not user.profile.portfolio_id:
        response = requests.post(f"{portfolio_api}/api/generate", json={
            "user_id": str(user.id),
            "basics": {
                "name": user.get_full_name(),
                "summary": user.profile.bio,
                "email": user.email
            }
        })
        
        if response.status_code == 201:
            result = response.json()
            user.profile.portfolio_id = result['portfolio_id']
            user.profile.save()
    
    return render(request, 'portfolio/edit.html', {
        'editor_url': f"{portfolio_api}/editor/{user.profile.portfolio_id}"
    })
```

### Exemple 2: JobsMatch avec React

```javascript
// PortfolioEditor.jsx
import React, { useEffect, useRef } from 'react';

function PortfolioEditor({ user, portfolioId }) {
    const iframeRef = useRef(null);
    const API_URL = 'https://portfolio-api.example.com';
    
    useEffect(() => {
        // Écouter les messages
        const handleMessage = (event) => {
            if (event.origin !== API_URL) return;
            
            if (event.data.type === 'portfolio-generated') {
                // Sauvegarder
                fetch('/api/portfolio/save', {
                    method: 'POST',
                    body: JSON.stringify(event.data.data)
                });
            }
        };
        
        window.addEventListener('message', handleMessage);
        return () => window.removeEventListener('message', handleMessage);
    }, []);
    
    const handleLoad = () => {
        // Pré-remplir avec les données utilisateur
        iframeRef.current.contentWindow.postMessage({
            type: 'prefill-data',
            data: {
                basics: {
                    name: user.fullName,
                    summary: user.bio,
                    email: user.email
                }
            }
        }, API_URL);
    };
    
    return (
        <div className="portfolio-editor">
            <h2>Mon Portfolio</h2>
            <iframe
                ref={iframeRef}
                src={`${API_URL}/editor/${portfolioId}`}
                width="100%"
                height="800px"
                onLoad={handleLoad}
            />
        </div>
    );
}
```

## 📚 Ressources

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentation API complète
- [jobsmatch_integration_example.py](jobsmatch_integration_example.py) - Exemples Python
- [test_api_server.py](test_api_server.py) - Tests API
- [README.md](README.md) - Documentation principale

## 💡 Bonnes Pratiques

1. **Toujours valider les origines** dans PostMessage
2. **Utiliser HTTPS** en production
3. **Implémenter l'authentification** pour l'API
4. **Rate limiting** pour éviter les abus
5. **Logs et monitoring** pour le debugging
6. **Sauvegardes régulières** des portfolios générés
7. **Tests automatisés** pour l'intégration
8. **Documentation claire** pour les développeurs externes

## ❓ FAQ

**Q: Peut-on héberger l'éditeur sur notre propre domaine?**
R: Oui, copiez `manual_editor.html` sur votre serveur. Assurez-vous de configurer CORS correctement.

**Q: Comment gérer les mises à jour en temps réel?**
R: Utilisez webhooks ou polling pour synchroniser les changements entre JobsMatch et les portfolios.

**Q: Les portfolios sont-ils stockés?**
R: Oui, dans le dossier `generated_portfolios/`. Pour la production, utilisez un stockage persistant (S3, etc.).

**Q: Peut-on personnaliser l'éditeur?**
R: Oui, modifiez `manual_editor.html` selon vos besoins. C'est un fichier HTML standalone.

**Q: Support multi-utilisateurs?**
R: Oui, chaque utilisateur a un `portfolio_id` unique. Utilisez une base de données pour tracker les associations.

## 🆘 Support

Pour toute question:
- GitHub Issues: https://github.com/pcx-wave/portfolio-generator/issues
- Documentation: Ce fichier et API_DOCUMENTATION.md
