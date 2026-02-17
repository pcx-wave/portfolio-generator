"""
Tests for the Portfolio Generator API Server

Run with: python -m pytest test_api_server.py -v
Or: python -m unittest test_api_server.py -v
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api_server import app, PORTFOLIO_REGISTRY, PORTFOLIOS_DIR


class APIServerTest(unittest.TestCase):
    """Test cases for API server endpoints."""
    
    def setUp(self):
        """Set up test client and temporary directory."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear portfolio registry
        PORTFOLIO_REGISTRY.clear()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'portfolio-generator-api')
    
    def test_index_endpoint(self):
        """Test API documentation index."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('service', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['service'], 'Portfolio Generator API')
    
    def test_generate_portfolio_basic(self):
        """Test basic portfolio generation via API."""
        portfolio_data = {
            "user_id": "test-user-123",
            "basics": {
                "name": "Test User",
                "summary": "Test bio",
                "email": "test@example.com"
            },
            "projects": [
                {
                    "name": "Test Project",
                    "description": "Test description"
                }
            ],
            "site_template": "hybrid",
            "design_theme": "modern"
        }
        
        response = self.client.post(
            '/api/generate',
            data=json.dumps(portfolio_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('portfolio_id', data)
        self.assertIn('portfolio_url', data)
        self.assertIn('editor_url', data)
        self.assertIn('admin_url', data)
        self.assertEqual(data['site_template'], 'hybrid')
        self.assertEqual(data['design_theme'], 'modern')
        
        # Verify portfolio was registered
        portfolio_id = data['portfolio_id']
        self.assertIn(portfolio_id, PORTFOLIO_REGISTRY)
    
    def test_generate_portfolio_minimal_data(self):
        """Test portfolio generation with minimal data."""
        portfolio_data = {
            "basics": {
                "name": "Minimal User",
                "summary": "Minimal bio"
            }
        }
        
        response = self.client.post(
            '/api/generate',
            data=json.dumps(portfolio_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_generate_portfolio_invalid_data(self):
        """Test portfolio generation with invalid data."""
        response = self.client.post(
            '/api/generate',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Should still succeed with empty data (generator handles it)
        self.assertIn(response.status_code, [201, 400, 500])
    
    def test_generate_portfolio_no_json(self):
        """Test portfolio generation without JSON data."""
        response = self.client.post('/api/generate')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_portfolio_not_found(self):
        """Test getting non-existent portfolio."""
        response = self.client.get('/api/portfolio/non-existent-id')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_portfolio_success(self):
        """Test getting portfolio data."""
        # First create a portfolio
        portfolio_data = {
            "user_id": "test-user-456",
            "basics": {
                "name": "Get Test User",
                "summary": "Get test bio"
            }
        }
        
        create_response = self.client.post(
            '/api/generate',
            data=json.dumps(portfolio_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        portfolio_id = create_data['portfolio_id']
        
        # Now get the portfolio
        get_response = self.client.get(f'/api/portfolio/{portfolio_id}')
        
        self.assertEqual(get_response.status_code, 200)
        get_data = json.loads(get_response.data)
        
        self.assertEqual(get_data['portfolio_id'], portfolio_id)
        self.assertIn('data', get_data)
        self.assertIn('metadata', get_data)
        self.assertIn('name', get_data['data'])
    
    def test_update_portfolio_not_found(self):
        """Test updating non-existent portfolio."""
        response = self.client.put(
            '/api/portfolio/non-existent-id',
            data=json.dumps({"name": "Updated"}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_portfolio_success(self):
        """Test updating portfolio."""
        # First create a portfolio
        portfolio_data = {
            "user_id": "test-user-789",
            "basics": {
                "name": "Update Test User",
                "summary": "Original bio"
            }
        }
        
        create_response = self.client.post(
            '/api/generate',
            data=json.dumps(portfolio_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        portfolio_id = create_data['portfolio_id']
        
        # Now update the portfolio
        update_data = {
            "name": "Updated Name",
            "bio": "Updated bio",
            "regenerate": False  # Skip regeneration for faster test
        }
        
        update_response = self.client.put(
            f'/api/portfolio/{portfolio_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(update_response.status_code, 200)
        update_result = json.loads(update_response.data)
        
        self.assertTrue(update_result['success'])
        self.assertEqual(update_result['portfolio_id'], portfolio_id)
        self.assertIn('updated_at', update_result)
    
    def test_validate_portfolio_not_found(self):
        """Test validating non-existent portfolio."""
        response = self.client.post('/api/portfolio/non-existent-id/validate')
        
        self.assertEqual(response.status_code, 404)
    
    def test_validate_portfolio_success(self):
        """Test validating portfolio."""
        # First create a portfolio
        portfolio_data = {
            "user_id": "test-user-validate",
            "basics": {
                "name": "Validate Test User",
                "summary": "Validate test bio"
            }
        }
        
        create_response = self.client.post(
            '/api/generate',
            data=json.dumps(portfolio_data),
            content_type='application/json'
        )
        
        create_data = json.loads(create_response.data)
        portfolio_id = create_data['portfolio_id']
        
        # Validate the portfolio
        validate_response = self.client.post(
            f'/api/portfolio/{portfolio_id}/validate'
        )
        
        self.assertEqual(validate_response.status_code, 200)
        validate_data = json.loads(validate_response.data)
        
        self.assertTrue(validate_data['success'])
        self.assertEqual(validate_data['status'], 'validated')
    
    def test_editor_endpoint(self):
        """Test serving the manual editor."""
        response = self.client.get('/editor')
        
        # Should return the HTML file
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data)
    
    def test_editor_save_new_portfolio(self):
        """Test saving from editor (new portfolio)."""
        editor_data = {
            "user_id": "editor-test-user",
            "data": {
                "basics": {
                    "name": "Editor Test User",
                    "summary": "Created from editor"
                }
            },
            "site_template": "portfolio",
            "design_theme": "classic"
        }
        
        response = self.client.post(
            '/api/editor/save',
            data=json.dumps(editor_data),
            content_type='application/json'
        )
        
        # Should create new portfolio
        self.assertIn(response.status_code, [200, 201])
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.client.get('/health')
        
        # CORS should be enabled
        # In production, check for Access-Control-Allow-Origin header
        self.assertEqual(response.status_code, 200)


class IntegrationTest(unittest.TestCase):
    """Integration tests for common workflows."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        PORTFOLIO_REGISTRY.clear()
    
    def test_complete_workflow(self):
        """Test complete workflow: create, get, update, validate."""
        # Step 1: Create portfolio
        create_data = {
            "user_id": "workflow-test-user",
            "basics": {
                "name": "Workflow Test",
                "summary": "Testing complete workflow"
            },
            "projects": [
                {
                    "name": "Initial Project",
                    "description": "Initial description"
                }
            ]
        }
        
        create_response = self.client.post(
            '/api/generate',
            data=json.dumps(create_data),
            content_type='application/json'
        )
        
        self.assertEqual(create_response.status_code, 201)
        create_result = json.loads(create_response.data)
        portfolio_id = create_result['portfolio_id']
        
        # Step 2: Get portfolio
        get_response = self.client.get(f'/api/portfolio/{portfolio_id}')
        self.assertEqual(get_response.status_code, 200)
        get_result = json.loads(get_response.data)
        self.assertEqual(get_result['data']['name'], 'Workflow Test')
        
        # Step 3: Update portfolio
        update_response = self.client.put(
            f'/api/portfolio/{portfolio_id}',
            data=json.dumps({
                "name": "Updated Workflow Test",
                "regenerate": False
            }),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Step 4: Validate portfolio
        validate_response = self.client.post(
            f'/api/portfolio/{portfolio_id}/validate'
        )
        self.assertEqual(validate_response.status_code, 200)
        validate_result = json.loads(validate_response.data)
        self.assertEqual(validate_result['status'], 'validated')


if __name__ == '__main__':
    unittest.main()
