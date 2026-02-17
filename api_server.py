"""
Flask API Server for Remote Portfolio Management

This server enables external systems (like JobsMatch) to:
- Generate portfolios remotely via API
- Retrieve and update portfolio data
- Serve the manual editor for remote editing
- Receive callbacks when portfolios are updated

Usage:
    python api_server.py

API Endpoints:
    POST /api/generate - Generate a new portfolio
    GET /api/portfolio/<portfolio_id> - Get portfolio data
    PUT /api/portfolio/<portfolio_id> - Update portfolio
    GET /editor - Serve manual editor
    GET /editor/<portfolio_id> - Serve editor with pre-filled data
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from generate_portfolio import generate_portfolio, mark_site_validated

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
PORTFOLIOS_DIR = Path(os.getenv("PORTFOLIOS_DIR", "generated_portfolios"))
PORTFOLIOS_DIR.mkdir(exist_ok=True)

# In-memory portfolio registry (use database in production)
PORTFOLIO_REGISTRY: Dict[str, Dict[str, Any]] = {}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "portfolio-generator-api"})


@app.route("/api/generate", methods=["POST"])
def api_generate_portfolio():
    """
    Generate a new portfolio from JSON data.
    
    Request body:
    {
        "user_id": "user-123",  # Optional, will be generated if not provided
        "basics": {...},
        "projects": [...],
        "skills": [...],
        "education": [...],
        "site_template": "hybrid",  # Optional: portfolio, cv, hybrid
        "design_theme": "classic",  # Optional: classic, modern, contrast, artistic
        "callback_url": "https://jobsmatch.com/api/portfolio-created"  # Optional
    }
    
    Response:
    {
        "success": true,
        "portfolio_id": "abc-123",
        "portfolio_url": "/portfolios/abc-123/index.html",
        "editor_url": "/editor/abc-123",
        "admin_url": "/portfolios/abc-123/admin/",
        "data_url": "/api/portfolio/abc-123"
    }
    """
    try:
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract configuration
        user_id = data.get("user_id", "")
        site_template = data.get("site_template", "hybrid")
        design_theme = data.get("design_theme", "classic")
        callback_url = data.get("callback_url")
        
        # Remove config fields from portfolio data
        portfolio_data = {k: v for k, v in data.items() 
                         if k not in ["site_template", "design_theme", "callback_url"]}
        
        # Generate portfolio
        output_dir = PORTFOLIOS_DIR / (user_id if user_id else f"portfolio-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        result = generate_portfolio(
            portfolio_data,
            output_dir=str(output_dir),
            site_template=site_template,
            design_theme=design_theme
        )
        
        portfolio_id = result["portfolio_id"]
        
        # Register portfolio
        PORTFOLIO_REGISTRY[portfolio_id] = {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "path": result["path"],
            "site_template": site_template,
            "design_theme": design_theme,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "callback_url": callback_url
        }
        
        # Build response
        response = {
            "success": True,
            "portfolio_id": portfolio_id,
            "portfolio_url": f"/portfolios/{Path(result['path']).name}/index.html",
            "editor_url": f"/editor/{portfolio_id}",
            "admin_url": f"/portfolios/{Path(result['path']).name}/admin/",
            "data_url": f"/api/portfolio/{portfolio_id}",
            "site_template": site_template,
            "design_theme": design_theme
        }
        
        # TODO: Send callback if callback_url provided
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio/<portfolio_id>", methods=["GET"])
def api_get_portfolio(portfolio_id):
    """
    Get portfolio data by ID.
    
    Response:
    {
        "portfolio_id": "abc-123",
        "data": {...},  # Full portfolio JSON
        "metadata": {...}
    }
    """
    try:
        if portfolio_id not in PORTFOLIO_REGISTRY:
            return jsonify({"error": "Portfolio not found"}), 404
        
        registry_entry = PORTFOLIO_REGISTRY[portfolio_id]
        portfolio_path = Path(registry_entry["path"])
        
        # Read portfolio data
        data_file = portfolio_path / "data" / "portfolio.json"
        if not data_file.exists():
            return jsonify({"error": "Portfolio data file not found"}), 404
        
        with open(data_file, "r", encoding="utf-8") as f:
            portfolio_data = json.load(f)
        
        return jsonify({
            "portfolio_id": portfolio_id,
            "data": portfolio_data,
            "metadata": {
                "user_id": registry_entry["user_id"],
                "site_template": registry_entry["site_template"],
                "design_theme": registry_entry["design_theme"],
                "created_at": registry_entry["created_at"],
                "portfolio_url": f"/portfolios/{portfolio_path.name}/index.html"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio/<portfolio_id>", methods=["PUT"])
def api_update_portfolio(portfolio_id):
    """
    Update an existing portfolio.
    
    Request body:
    {
        "basics": {...},
        "projects": [...],
        ...
        "regenerate": true  # Optional: regenerate HTML (default: true)
    }
    
    Response:
    {
        "success": true,
        "portfolio_id": "abc-123",
        "updated_at": "2026-02-17T15:30:00Z"
    }
    """
    try:
        if portfolio_id not in PORTFOLIO_REGISTRY:
            return jsonify({"error": "Portfolio not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        registry_entry = PORTFOLIO_REGISTRY[portfolio_id]
        portfolio_path = Path(registry_entry["path"])
        
        # Update portfolio data file
        data_file = portfolio_path / "data" / "portfolio.json"
        
        # Read current data
        with open(data_file, "r", encoding="utf-8") as f:
            current_data = json.load(f)
        
        # Merge with new data (preserve project_ids)
        current_data.update(data)
        
        # Write updated data
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        
        # Regenerate HTML if requested
        regenerate = data.get("regenerate", True)
        if regenerate:
            # Rebuild portfolio data in the correct format
            portfolio_data = {
                "basics": {
                    "name": current_data.get("name", ""),
                    "summary": current_data.get("bio", ""),
                    "label": current_data.get("headline"),
                    "image": current_data.get("photo_url"),
                    "email": current_data.get("contact_line", "").split("|")[0].strip() if "|" in current_data.get("contact_line", "") else None,
                    "profiles": current_data.get("profiles", [])
                },
                "skills": current_data.get("skills", []),
                "education": current_data.get("education", []),
                "projects": current_data.get("projects", [])
            }
            
            # Regenerate
            generate_portfolio(
                portfolio_data,
                output_dir=str(portfolio_path),
                site_template=registry_entry["site_template"],
                design_theme=registry_entry["design_theme"]
            )
        
        updated_at = datetime.now(timezone.utc).isoformat()
        
        return jsonify({
            "success": True,
            "portfolio_id": portfolio_id,
            "updated_at": updated_at
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/portfolio/<portfolio_id>/validate", methods=["POST"])
def api_validate_portfolio(portfolio_id):
    """
    Mark a portfolio as validated (ready for deployment).
    
    Response:
    {
        "success": true,
        "portfolio_id": "abc-123",
        "status": "validated"
    }
    """
    try:
        if portfolio_id not in PORTFOLIO_REGISTRY:
            return jsonify({"error": "Portfolio not found"}), 404
        
        registry_entry = PORTFOLIO_REGISTRY[portfolio_id]
        result = mark_site_validated(registry_entry["path"])
        
        return jsonify({
            "success": True,
            "portfolio_id": portfolio_id,
            "status": result["status"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/editor", methods=["GET"])
@app.route("/editor/<portfolio_id>", methods=["GET"])
def serve_editor(portfolio_id=None):
    """
    Serve the manual editor HTML.
    If portfolio_id is provided, pre-fill the editor with existing data.
    """
    editor_path = Path(__file__).parent / "manual_editor.html"
    
    if not editor_path.exists():
        return jsonify({"error": "Editor not found"}), 404
    
    # If portfolio_id provided, we'll need to modify the editor to support pre-filling
    # For now, just serve the editor
    return send_file(str(editor_path))


@app.route("/portfolios/<path:filename>")
def serve_portfolio(filename):
    """Serve generated portfolio files."""
    return send_from_directory(str(PORTFOLIOS_DIR), filename)


@app.route("/api/editor/save", methods=["POST"])
def api_editor_save():
    """
    Save data from the remote editor and generate/update portfolio.
    
    This endpoint is called when the editor's "Generate" button is clicked
    from a remote context (e.g., embedded in JobsMatch).
    
    Request body:
    {
        "portfolio_id": "abc-123",  # Optional: if updating existing
        "user_id": "user-123",
        "data": {...},  # Portfolio data
        "site_template": "hybrid",
        "design_theme": "classic",
        "return_url": "https://jobsmatch.com/profile"  # Optional: where to redirect after save
    }
    
    Response:
    {
        "success": true,
        "portfolio_id": "abc-123",
        "portfolio_url": "/portfolios/...",
        "return_url": "https://jobsmatch.com/profile?portfolio_id=abc-123"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        portfolio_id = request_data.get("portfolio_id")
        
        if portfolio_id and portfolio_id in PORTFOLIO_REGISTRY:
            # Update existing portfolio
            response = api_update_portfolio(portfolio_id)
            return response
        else:
            # Generate new portfolio
            return api_generate_portfolio()
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """API documentation."""
    return jsonify({
        "service": "Portfolio Generator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate": "Generate a new portfolio",
            "GET /api/portfolio/<id>": "Get portfolio data",
            "PUT /api/portfolio/<id>": "Update portfolio",
            "POST /api/portfolio/<id>/validate": "Validate portfolio",
            "GET /editor": "Serve manual editor",
            "GET /editor/<id>": "Serve editor with pre-filled data",
            "POST /api/editor/save": "Save data from remote editor",
            "GET /portfolios/<path>": "Serve generated portfolio files",
            "GET /health": "Health check"
        },
        "documentation": "/docs"
    })


@app.route("/docs", methods=["GET"])
def documentation():
    """Detailed API documentation."""
    return send_file(str(Path(__file__).parent / "API_DOCUMENTATION.md"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Portfolio Generator API Server")
    print(f"📡 Starting on http://localhost:{port}")
    print(f"📝 API Docs: http://localhost:{port}/docs")
    print(f"🎨 Editor: http://localhost:{port}/editor")
    print(f"💾 Portfolios directory: {PORTFOLIOS_DIR.absolute()}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
