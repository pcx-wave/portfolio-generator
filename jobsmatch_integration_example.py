"""
Example Integration Code for JobsMatch

This file demonstrates how JobsMatch can integrate with the Portfolio Generator API
to enable users to create and manage their portfolios.
"""

import requests
from typing import Dict, Any, Optional


class PortfolioAPIClient:
    """Client for Portfolio Generator API."""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url.rstrip('/')
    
    def create_portfolio(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        site_template: str = "hybrid",
        design_theme: str = "modern",
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a portfolio for a JobsMatch user.
        
        Args:
            user_id: JobsMatch user ID
            user_data: User data from JobsMatch database
            site_template: Portfolio template (portfolio, cv, hybrid)
            design_theme: Design theme (classic, modern, contrast, artistic)
            callback_url: URL to notify when portfolio is created
        
        Returns:
            API response with portfolio URLs
        """
        # Transform JobsMatch data to portfolio format
        portfolio_data = {
            "user_id": user_id,
            "basics": {
                "name": user_data.get("full_name", ""),
                "summary": user_data.get("bio", ""),
                "label": user_data.get("job_title", ""),
                "email": user_data.get("email", ""),
                "phone": user_data.get("phone", ""),
                "image": user_data.get("profile_photo_url", ""),
                "location": {
                    "address": user_data.get("address", "")
                },
                "profiles": self._transform_social_profiles(user_data.get("social_profiles", []))
            },
            "skills": [{"name": skill} for skill in user_data.get("skills", [])],
            "education": self._transform_education(user_data.get("education", [])),
            "projects": self._transform_projects(user_data.get("projects", [])),
            "site_template": site_template,
            "design_theme": design_theme
        }
        
        if callback_url:
            portfolio_data["callback_url"] = callback_url
        
        response = requests.post(
            f"{self.api_base_url}/api/generate",
            json=portfolio_data
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """Get portfolio data by ID."""
        response = requests.get(
            f"{self.api_base_url}/api/portfolio/{portfolio_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def update_portfolio(
        self,
        portfolio_id: str,
        updated_data: Dict[str, Any],
        regenerate: bool = True
    ) -> Dict[str, Any]:
        """Update an existing portfolio."""
        data = {**updated_data, "regenerate": regenerate}
        
        response = requests.put(
            f"{self.api_base_url}/api/portfolio/{portfolio_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def validate_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """Mark portfolio as validated."""
        response = requests.post(
            f"{self.api_base_url}/api/portfolio/{portfolio_id}/validate"
        )
        response.raise_for_status()
        return response.json()
    
    def get_editor_url(self, portfolio_id: Optional[str] = None) -> str:
        """Get URL to the manual editor."""
        if portfolio_id:
            return f"{self.api_base_url}/editor/{portfolio_id}"
        return f"{self.api_base_url}/editor"
    
    def _transform_social_profiles(self, profiles: list) -> list:
        """Transform JobsMatch social profiles to portfolio format."""
        return [
            {
                "network": profile.get("platform", ""),
                "url": profile.get("url", "")
            }
            for profile in profiles
        ]
    
    def _transform_education(self, education: list) -> list:
        """Transform JobsMatch education data to portfolio format."""
        return [
            {
                "institution": edu.get("school_name", ""),
                "studyType": edu.get("degree_type", ""),
                "area": edu.get("field_of_study", ""),
                "startDate": str(edu.get("start_year", "")),
                "endDate": str(edu.get("end_year", "")),
                "score": edu.get("gpa", "")
            }
            for edu in education
        ]
    
    def _transform_projects(self, projects: list) -> list:
        """Transform JobsMatch projects to portfolio format."""
        return [
            {
                "name": project.get("title", ""),
                "description": project.get("description", ""),
                "image": project.get("image_url", "")
            }
            for project in projects
        ]


# Example Usage Scenarios

def example_1_create_portfolio_on_registration():
    """Example 1: Create portfolio when user registers on JobsMatch."""
    
    # Initialize API client
    client = PortfolioAPIClient("http://portfolio-api.example.com")
    
    # Simulated user data from JobsMatch registration
    user_data = {
        "id": "jobsmatch-user-123",
        "full_name": "Alice Johnson",
        "bio": "Full-stack developer with 5 years of experience in React and Node.js",
        "job_title": "Senior Full-Stack Developer",
        "email": "alice@example.com",
        "phone": "+1 234 567 8900",
        "profile_photo_url": "https://jobsmatch.com/photos/alice.jpg",
        "address": "123 Tech Street, San Francisco, CA",
        "social_profiles": [
            {"platform": "LinkedIn", "url": "https://linkedin.com/in/alicejohnson"},
            {"platform": "GitHub", "url": "https://github.com/alicejohnson"}
        ],
        "skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB"],
        "education": [
            {
                "school_name": "Stanford University",
                "degree_type": "Bachelor",
                "field_of_study": "Computer Science",
                "start_year": 2015,
                "end_year": 2019,
                "gpa": "3.8"
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "description": "Built a scalable e-commerce platform serving 10k+ users",
                "image_url": "https://jobsmatch.com/projects/ecommerce.jpg"
            }
        ]
    }
    
    # Create portfolio
    result = client.create_portfolio(
        user_id=user_data["id"],
        user_data=user_data,
        site_template="hybrid",
        design_theme="modern",
        callback_url="https://jobsmatch.com/api/webhook/portfolio-created"
    )
    
    print(f"Portfolio created successfully!")
    print(f"Portfolio ID: {result['portfolio_id']}")
    print(f"Portfolio URL: {result['portfolio_url']}")
    print(f"Editor URL: {result['editor_url']}")
    
    # Save portfolio_id in JobsMatch database
    # db.users.update_one(
    #     {"id": user_data["id"]},
    #     {"$set": {"portfolio_id": result["portfolio_id"]}}
    # )
    
    return result


def example_2_update_portfolio_on_profile_change():
    """Example 2: Update portfolio when user updates their JobsMatch profile."""
    
    client = PortfolioAPIClient("http://portfolio-api.example.com")
    
    portfolio_id = "abc-123-def-456"  # Retrieved from JobsMatch database
    
    # User updated their bio and added a new skill
    updated_data = {
        "bio": "Updated bio: Full-stack developer with 6 years of experience",
        "skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB", "TypeScript"]
    }
    
    result = client.update_portfolio(
        portfolio_id=portfolio_id,
        updated_data=updated_data,
        regenerate=True
    )
    
    print(f"Portfolio updated: {result['portfolio_id']}")
    return result


def example_3_embed_editor_in_jobsmatch():
    """Example 3: Embed the portfolio editor in JobsMatch's UI."""
    
    # This would be in your JobsMatch HTML template
    html_template = """
    <div class="portfolio-section">
        <h2>Your Portfolio</h2>
        <p>Edit your portfolio to showcase your work to potential employers.</p>
        
        <div id="portfolio-editor-container">
            <iframe 
                id="portfolio-editor-frame"
                src="http://portfolio-api.example.com/editor/{portfolio_id}"
                width="100%" 
                height="800px"
                frameborder="0"
                style="border: 1px solid #ccc; border-radius: 8px;">
            </iframe>
        </div>
    </div>
    
    <script>
        // Listen for messages from the editor
        window.addEventListener('message', function(event) {
            if (event.origin !== "http://portfolio-api.example.com") return;
            
            if (event.data.type === 'portfolio-generated') {
                console.log('Portfolio generated:', event.data.data);
                
                // Save the generated portfolio data
                fetch('/api/save-portfolio', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        portfolio_data: event.data.data
                    })
                });
                
                // Show success message
                showSuccessMessage('Portfolio saved successfully!');
            }
        });
        
        // Pre-fill editor with user data
        window.onload = function() {
            const editorFrame = document.getElementById('portfolio-editor-frame');
            
            editorFrame.onload = function() {
                // Send user data to editor
                editorFrame.contentWindow.postMessage({
                    type: 'prefill-data',
                    data: {{ user_portfolio_data | tojson }}
                }, '*');
            };
        };
    </script>
    """
    
    return html_template


def example_4_direct_api_link():
    """Example 4: Provide direct link to editor from JobsMatch."""
    
    client = PortfolioAPIClient("http://portfolio-api.example.com")
    
    # Get editor URL with pre-filled data
    user_id = "jobsmatch-user-123"
    portfolio_id = "abc-123-def-456"  # If user already has a portfolio
    
    editor_url = client.get_editor_url(portfolio_id)
    
    # Or create a link with URL parameters
    import urllib.parse
    user_data = {
        "basics": {
            "name": "Alice Johnson",
            "summary": "Full-stack developer"
        }
    }
    
    data_param = urllib.parse.quote(json.dumps(user_data))
    editor_url_with_data = f"{client.api_base_url}/editor?data={data_param}"
    
    print(f"Editor URL: {editor_url}")
    print(f"Editor with data: {editor_url_with_data}")
    
    return editor_url


def example_5_webhook_handler():
    """Example 5: Handle webhook callbacks in JobsMatch."""
    
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route("/api/webhook/portfolio-created", methods=["POST"])
    def handle_portfolio_created():
        """Handle portfolio creation callback."""
        data = request.get_json()
        
        portfolio_id = data.get("portfolio_id")
        user_id = data.get("user_id")
        portfolio_url = data.get("portfolio_url")
        
        # Update user record in JobsMatch database
        # db.users.update_one(
        #     {"id": user_id},
        #     {"$set": {
        #         "portfolio_id": portfolio_id,
        #         "portfolio_url": portfolio_url,
        #         "portfolio_created_at": datetime.now()
        #     }}
        # )
        
        # Send email notification to user
        # send_email(
        #     to=user_email,
        #     subject="Your portfolio is ready!",
        #     body=f"View your portfolio at: {portfolio_url}"
        # )
        
        print(f"Portfolio created for user {user_id}: {portfolio_url}")
        
        return jsonify({"status": "received"}), 200
    
    return app


# Django Integration Example
def django_integration_example():
    """Example integration with Django-based JobsMatch."""
    
    example_code = """
    # jobsmatch/portfolio/views.py
    from django.shortcuts import render, redirect
    from django.contrib.auth.decorators import login_required
    from .portfolio_client import PortfolioAPIClient
    
    @login_required
    def create_portfolio(request):
        '''Create portfolio for logged-in user.'''
        client = PortfolioAPIClient(settings.PORTFOLIO_API_URL)
        
        user_data = {
            "id": str(request.user.id),
            "full_name": request.user.get_full_name(),
            "bio": request.user.profile.bio,
            "email": request.user.email,
            # ... other fields
        }
        
        result = client.create_portfolio(
            user_id=str(request.user.id),
            user_data=user_data
        )
        
        # Save portfolio ID
        request.user.profile.portfolio_id = result['portfolio_id']
        request.user.profile.portfolio_url = result['portfolio_url']
        request.user.profile.save()
        
        return redirect('portfolio_success')
    
    @login_required
    def edit_portfolio(request):
        '''Show embedded portfolio editor.'''
        portfolio_id = request.user.profile.portfolio_id
        
        return render(request, 'portfolio/edit.html', {
            'portfolio_id': portfolio_id,
            'editor_url': f"{settings.PORTFOLIO_API_URL}/editor/{portfolio_id}"
        })
    """
    
    return example_code


if __name__ == "__main__":
    # Run examples
    import json
    
    print("=" * 60)
    print("Example 1: Create Portfolio on Registration")
    print("=" * 60)
    try:
        result = example_1_create_portfolio_on_registration()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Example 4: Direct API Link")
    print("=" * 60)
    editor_url = example_4_direct_api_link()
