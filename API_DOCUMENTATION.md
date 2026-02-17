# Portfolio Generator API Documentation

## Overview

The Portfolio Generator API enables remote portfolio management for external systems like JobsMatch. It provides REST endpoints for creating, updating, and managing portfolios programmatically.

## Base URL

```
http://localhost:5000
```

For production, replace with your deployed URL.

## ⚠️ Security Warning

**IMPORTANT:** The example configuration is intended **only for local development on a trusted machine**. The API is currently "open" without authentication.

Before exposing this API beyond localhost (e.g., in staging or production), you **must**:
- Enable strong authentication and authorization (such as API keys or OAuth with per-user/tenant access control)
- Ensure that all portfolio management endpoints enforce authentication consistently
- Configure CORS to restrict allowed origins via the `API_ALLOWED_ORIGINS` environment variable
- Use HTTPS for all production deployments

**Running this API "open" on any network-accessible host is unsafe and must not be done with real user data.**

## Authentication

Currently, the API is open. For production use, implement authentication (API keys, OAuth, etc.).

## Endpoints

### 1. Generate Portfolio

Generate a new portfolio from JSON data.

**Endpoint:** `POST /api/generate`

**Request Body:**
```json
{
  "user_id": "user-123",
  "basics": {
    "name": "John Doe",
    "summary": "Full-stack developer",
    "label": "Senior Developer",
    "email": "john@example.com",
    "phone": "+1 234 567 8900",
    "image": "https://example.com/photo.jpg",
    "location": {
      "address": "123 Main St, City, Country"
    },
    "profiles": [
      {
        "network": "LinkedIn",
        "url": "https://linkedin.com/in/johndoe"
      }
    ]
  },
  "skills": [
    {"name": "JavaScript"},
    {"name": "Python"}
  ],
  "education": [
    {
      "institution": "University Name",
      "studyType": "Bachelor",
      "area": "Computer Science",
      "startDate": "2015",
      "endDate": "2019"
    }
  ],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built a scalable e-commerce platform",
      "image": "https://example.com/project.jpg"
    }
  ],
  "site_template": "hybrid",
  "design_theme": "modern",
  "callback_url": "https://jobsmatch.com/api/webhook/portfolio-created"
}
```

**Parameters:**
- `user_id` (optional): User identifier
- `basics` (required): Basic information (name, summary, etc.)
- `skills` (optional): Array of skills
- `education` (optional): Array of education entries
- `projects` (optional): Array of projects
- `site_template` (optional): `portfolio`, `cv`, or `hybrid` (default: `hybrid`)
- `design_theme` (optional): `classic`, `modern`, `contrast`, or `artistic` (default: `classic`)
- `callback_url` (optional): URL to call when portfolio is created

**Response:** `201 Created`
```json
{
  "success": true,
  "portfolio_id": "abc-123-def-456",
  "portfolio_url": "/portfolios/user-123/index.html",
  "editor_url": "/editor/abc-123-def-456",
  "admin_url": "/portfolios/user-123/admin/",
  "data_url": "/api/portfolio/abc-123-def-456",
  "site_template": "hybrid",
  "design_theme": "modern"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d @portfolio_data.json
```

**Example (Python):**
```python
import requests

data = {
    "user_id": "user-123",
    "basics": {
        "name": "John Doe",
        "summary": "Full-stack developer"
    },
    "projects": [
        {
            "name": "My Project",
            "description": "Project description"
        }
    ],
    "site_template": "hybrid",
    "design_theme": "modern"
}

response = requests.post(
    "http://localhost:5000/api/generate",
    json=data
)

result = response.json()
print(f"Portfolio created: {result['portfolio_url']}")
```

**Example (JavaScript):**
```javascript
const data = {
  user_id: 'user-123',
  basics: {
    name: 'John Doe',
    summary: 'Full-stack developer'
  },
  projects: [
    {
      name: 'My Project',
      description: 'Project description'
    }
  ],
  site_template: 'hybrid',
  design_theme: 'modern'
};

fetch('http://localhost:5000/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
  console.log('Portfolio created:', result.portfolio_url);
});
```

---

### 2. Get Portfolio Data

Retrieve portfolio data by ID.

**Endpoint:** `GET /api/portfolio/{portfolio_id}`

**Response:** `200 OK`
```json
{
  "portfolio_id": "abc-123-def-456",
  "data": {
    "name": "John Doe",
    "bio": "Full-stack developer",
    "projects": [...],
    "skills": [...],
    "education": [...]
  },
  "metadata": {
    "user_id": "user-123",
    "site_template": "hybrid",
    "design_theme": "modern",
    "created_at": "2026-02-17T15:30:00Z",
    "portfolio_url": "/portfolios/user-123/index.html"
  }
}
```

**Example (cURL):**
```bash
curl http://localhost:5000/api/portfolio/abc-123-def-456
```

---

### 3. Update Portfolio

Update an existing portfolio.

**Endpoint:** `PUT /api/portfolio/{portfolio_id}`

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "bio": "Updated bio",
  "projects": [...],
  "regenerate": true
}
```

**Parameters:**
- `regenerate` (optional): Whether to regenerate HTML (default: `true`)

**Response:** `200 OK`
```json
{
  "success": true,
  "portfolio_id": "abc-123-def-456",
  "updated_at": "2026-02-17T16:00:00Z"
}
```

**Example (cURL):**
```bash
curl -X PUT http://localhost:5000/api/portfolio/abc-123-def-456 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "bio": "Updated bio"}'
```

---

### 4. Validate Portfolio

Mark a portfolio as validated (ready for deployment).

**Endpoint:** `POST /api/portfolio/{portfolio_id}/validate`

**Response:** `200 OK`
```json
{
  "success": true,
  "portfolio_id": "abc-123-def-456",
  "status": "validated"
}
```

---

### 5. Serve Manual Editor

Access the interactive manual editor.

**Endpoint:** `GET /editor`

Opens the manual editor in the browser.

**For Pre-filled Editor:**
**Endpoint:** `GET /editor/{portfolio_id}`

Opens the editor with existing portfolio data pre-filled.

---

### 6. Save from Remote Editor

Save data from the remote editor (called by the editor itself).

**Endpoint:** `POST /api/editor/save`

**Request Body:**
```json
{
  "portfolio_id": "abc-123-def-456",
  "user_id": "user-123",
  "data": {...},
  "site_template": "hybrid",
  "design_theme": "modern",
  "return_url": "https://jobsmatch.com/profile"
}
```

**Response:** `201 Created` or `200 OK`
```json
{
  "success": true,
  "portfolio_id": "abc-123-def-456",
  "portfolio_url": "/portfolios/user-123/index.html",
  "return_url": "https://jobsmatch.com/profile?portfolio_id=abc-123-def-456"
}
```

---

### 7. Serve Portfolio Files

Access generated portfolio files.

**Endpoint:** `GET /portfolios/{path}`

Example: `GET /portfolios/user-123/index.html`

---

### 8. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "portfolio-generator-api"
}
```

---

## Integration with JobsMatch

### Scenario 1: Generate Portfolio When User Registers

When a user registers on JobsMatch and provides their information, automatically create their portfolio:

```python
import requests

def create_user_portfolio(user_data):
    """Create portfolio for new JobsMatch user."""
    
    # Transform JobsMatch user data to portfolio format
    portfolio_data = {
        "user_id": user_data['id'],
        "basics": {
            "name": user_data['full_name'],
            "summary": user_data['bio'],
            "email": user_data['email'],
            "phone": user_data['phone']
        },
        "skills": [{"name": skill} for skill in user_data.get('skills', [])],
        "projects": user_data.get('projects', []),
        "site_template": "hybrid",
        "design_theme": "modern",
        "callback_url": f"https://jobsmatch.com/api/portfolio-callback"
    }
    
    response = requests.post(
        "http://portfolio-api.example.com/api/generate",
        json=portfolio_data
    )
    
    if response.status_code == 201:
        result = response.json()
        
        # Save portfolio URL in JobsMatch database
        save_portfolio_url(user_data['id'], result['portfolio_url'])
        
        return result
    else:
        raise Exception(f"Portfolio creation failed: {response.text}")
```

### Scenario 2: Let Users Edit Their Portfolio via Embedded Editor

Embed the editor in JobsMatch's UI:

```html
<!-- In JobsMatch profile page -->
<div id="portfolio-editor-container">
    <iframe 
        src="http://portfolio-api.example.com/editor/{portfolio_id}"
        width="100%" 
        height="800px"
        frameborder="0">
    </iframe>
</div>
```

### Scenario 3: Update Portfolio When User Updates Profile

When a user updates their JobsMatch profile, automatically update their portfolio:

```python
def update_user_portfolio(user_id, updated_data):
    """Update portfolio when JobsMatch profile is updated."""
    
    portfolio_id = get_portfolio_id_for_user(user_id)
    
    response = requests.put(
        f"http://portfolio-api.example.com/api/portfolio/{portfolio_id}",
        json={
            "name": updated_data.get('full_name'),
            "bio": updated_data.get('bio'),
            "regenerate": True
        }
    )
    
    return response.json()
```

### Scenario 4: Custom Integration with PostMessage API

For advanced iframe communication:

```javascript
// In JobsMatch (parent window)
const editorFrame = document.getElementById('portfolio-editor-frame');

// Listen for messages from editor
window.addEventListener('message', function(event) {
    if (event.data.type === 'portfolio-saved') {
        console.log('Portfolio saved:', event.data.portfolio_id);
        // Update JobsMatch UI
        updateUserPortfolioStatus(event.data.portfolio_id);
    }
});

// Send data to editor
editorFrame.contentWindow.postMessage({
    type: 'prefill-data',
    data: userData
}, '*');
```

---

## Deployment

### Local Development

```bash
# Install dependencies
pip install flask flask-cors

# Run server
python api_server.py

# Access at http://localhost:5000
```

### Production Deployment

#### Option 1: Using Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

#### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

Build and run:
```bash
docker build -t portfolio-api .
docker run -p 5000:5000 -v $(pwd)/generated_portfolios:/app/generated_portfolios portfolio-api
```

#### Option 3: Platform-as-a-Service (Heroku, Railway, etc.)

Create `Procfile`:
```
web: gunicorn api_server:app
```

Create `requirements.txt`:
```
flask>=2.0.0
flask-cors>=3.0.0
gunicorn>=20.0.0
```

Deploy:
```bash
git push heroku main
```

---

## Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: false)
- `PORTFOLIOS_DIR`: Directory for generated portfolios (default: generated_portfolios)

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Error message description"
}
```

---

## Rate Limiting

For production, implement rate limiting to prevent abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/api/generate", methods=["POST"])
@limiter.limit("10 per minute")
def api_generate_portfolio():
    # ...
```

---

## Security Considerations

1. **Authentication**: Implement API key or OAuth authentication
2. **Input Validation**: Validate all input data
3. **Rate Limiting**: Prevent abuse
4. **CORS**: Configure appropriate CORS policies
5. **HTTPS**: Use HTTPS in production
6. **File Access**: Restrict file system access
7. **Sanitization**: Sanitize HTML output (already implemented in generator)

---

## Support

For issues or questions:
- GitHub: https://github.com/pcx-wave/portfolio-generator
- Documentation: This file

---

## License

Same as the main portfolio-generator project (MIT).
