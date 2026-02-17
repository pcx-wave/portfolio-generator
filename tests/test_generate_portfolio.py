import json
import tempfile
import unittest
from pathlib import Path

from generate_portfolio import generate_portfolio, mark_site_validated, generate_astro_portfolio


class GeneratePortfolioTest(unittest.TestCase):
    def test_generates_static_site_with_decap_and_netlify_files(self) -> None:
        user_data = {
            "name": "Alice <Dev>",
            "bio": "Backend engineer",
            "projects": [{"title": "Proj 1", "description": "Desc", "image": "img.png"}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(user_data, output_dir=temp_dir)
            output = Path(result["path"])

            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "styles" / "main.css").exists())
            self.assertTrue((output / "admin" / "index.html").exists())
            self.assertTrue((output / "admin" / "config.yml").exists())
            self.assertTrue((output / "netlify.toml").exists())
            self.assertTrue((output / "data" / "portfolio_document.json").exists())
            self.assertTrue((output / "data" / "portfolio_sql_projection.json").exists())
            self.assertTrue((output / "data" / "workflow_state.json").exists())

            html_content = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Alice &lt;Dev&gt;", html_content)

            data_content = json.loads((output / "data" / "portfolio.json").read_text(encoding="utf-8"))
            self.assertEqual("Alice &lt;Dev&gt;", data_content["name"])
            self.assertEqual("Proj 1", data_content["projects"][0]["title"])

            document_content = json.loads((output / "data" / "portfolio_document.json").read_text(encoding="utf-8"))
            self.assertIn("portfolio_id", document_content)
            self.assertIn("project_id", document_content["projects"][0])

            sql_projection = json.loads((output / "data" / "portfolio_sql_projection.json").read_text(encoding="utf-8"))
            self.assertEqual(document_content["portfolio_id"], sql_projection["portfolios"][0]["portfolio_id"])
            self.assertEqual(document_content["projects"][0]["project_id"], sql_projection["projects"][0]["project_id"])

            workflow_state = json.loads((output / "data" / "workflow_state.json").read_text(encoding="utf-8"))
            self.assertEqual("draft", workflow_state["status"])
            self.assertEqual("hybrid", workflow_state["site_template"])

    def test_supports_design_theme_selection(self) -> None:
        user_data = {"name": "Theme User", "bio": "Bio", "projects": []}
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(user_data, output_dir=temp_dir, design_theme="modern")
            self.assertEqual("modern", result["design_theme"])
            css_content = (Path(temp_dir) / "styles" / "main.css").read_text(encoding="utf-8")
            self.assertIn("linear-gradient(135deg, var(--primary-color), var(--secondary-color))", css_content)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(user_data, output_dir=temp_dir, design_theme="artistic")
            self.assertEqual("artistic", result["design_theme"])
            css_content = (Path(temp_dir) / "styles" / "main.css").read_text(encoding="utf-8")
            self.assertIn("clip-path: polygon(0 0, 100% 0, 100% 90%, 0 100%);", css_content)

    def test_accepts_cv_augmented_input_format(self) -> None:
        cv_data = {
            "basics": {
                "name": "Marie Curie",
                "summary": "Data scientist",
                "label": "Senior Data Scientist",
                "email": "marie@example.com",
                "phone": "+33 6 12 34 56 78",
                "image": "https://example.com/marie.jpg",
                "location": {
                    "address": "1 rue des Sciences",
                    "postalCode": "75005",
                    "city": "Paris",
                    "region": "IDF",
                    "countryCode": "FR",
                },
                "profiles": [{"network": "LinkedIn", "url": "https://linkedin.com/in/marie"}],
            },
            "work": [
                {
                    "name": "LabX",
                    "position": "ML Engineer",
                    "summary": "Built ranking models",
                    "highlights": ["Improved precision", "Reduced latency"],
                }
            ],
            "education": [
                {
                    "institution": "Sorbonne",
                    "studyType": "Master",
                    "area": "Data Science",
                    "startDate": "2018",
                    "endDate": "2020",
                    "score": "16/20",
                }
            ],
            "skills": [{"name": "Python", "keywords": ["Pandas", "Scikit-learn"]}],
            "projects": [{"name": "Matching API", "description": "API for recommendations", "image": ""}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(cv_data, output_dir=temp_dir)
            output = Path(result["path"])

            data_content = json.loads((output / "data" / "portfolio.json").read_text(encoding="utf-8"))
            self.assertEqual("Marie Curie", data_content["name"])
            self.assertEqual("Data scientist", data_content["bio"])
            self.assertEqual(2, len(data_content["projects"]))
            self.assertEqual("Matching API", data_content["projects"][0]["title"])
            self.assertEqual("ML Engineer - LabX", data_content["projects"][1]["title"])
            self.assertEqual("https://example.com/marie.jpg", data_content["photo_url"])
            self.assertIn("marie@example.com", data_content["contact_line"])
            self.assertEqual("1 rue des Sciences | 75005 Paris | IDF | FR", data_content["address_line"])
            self.assertEqual("Sorbonne", data_content["education"][0]["institution"])

            html_content = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Senior Data Scientist", html_content)
            self.assertIn("LinkedIn", html_content)
            self.assertIn("Master - Data Science", html_content)

    def test_supports_template_selection_and_validation_state(self) -> None:
        cv_data = {
            "basics": {"name": "Jean Dupont", "summary": "Ingénieur logiciel"},
            "work": [{"name": "Startup", "position": "Backend Engineer", "summary": "Built APIs"}],
            "projects": [{"name": "Portfolio UI", "description": "Showcase app", "image": ""}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(cv_data, output_dir=temp_dir, site_template="cv")
            output = Path(result["path"])

            data_content = json.loads((output / "data" / "portfolio.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(data_content["projects"]))
            self.assertEqual("Backend Engineer - Startup", data_content["projects"][0]["title"])

            html_content = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("<h2>Expériences</h2>", html_content)

            validation_result = mark_site_validated(str(output))
            self.assertEqual("validated", validation_result["status"])
            workflow_state = json.loads((output / "data" / "workflow_state.json").read_text(encoding="utf-8"))
            self.assertEqual("validated", workflow_state["status"])
            self.assertIn("validated_at", workflow_state)

        with tempfile.TemporaryDirectory() as temp_dir:
            generate_portfolio(cv_data, output_dir=temp_dir, site_template="portfolio")
            html_content = (Path(temp_dir) / "index.html").read_text(encoding="utf-8")
            self.assertIn("<h2>Réalisations</h2>", html_content)

        with tempfile.TemporaryDirectory() as temp_dir:
            generate_portfolio(cv_data, output_dir=temp_dir, site_template="hybrid")
            html_content = (Path(temp_dir) / "index.html").read_text(encoding="utf-8")
            self.assertIn("<h2>Réalisations & Expériences</h2>", html_content)

    def test_manual_editor_json_format_compatibility(self) -> None:
        """Test that JSON format from manual editor works with portfolio generator."""
        manual_editor_data = {
            "basics": {
                "name": "Test User",
                "summary": "Test bio summary",
                "label": "Test Label",
                "image": "https://example.com/photo.jpg",
                "email": "test@example.com",
                "phone": "+33 6 00 00 00 00",
                "location": {
                    "address": "1 rue Test, 75001 Paris"
                },
                "profiles": [
                    {"network": "LinkedIn", "url": "https://linkedin.com/in/test"}
                ]
            },
            "skills": [
                {"name": "Skill 1"},
                {"name": "Skill 2"}
            ],
            "education": [
                {
                    "institution": "Test University",
                    "studyType": "Master",
                    "area": "Computer Science",
                    "startDate": "2020",
                    "endDate": "2022",
                    "score": "Excellent"
                }
            ],
            "projects": [
                {
                    "name": "Test Project",
                    "description": "Test project description",
                    "image": "https://example.com/project.jpg"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(manual_editor_data, output_dir=temp_dir)
            output = Path(result["path"])
            
            # Verify all files are generated
            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "data" / "portfolio.json").exists())
            
            # Verify data is correctly processed
            data_content = json.loads((output / "data" / "portfolio.json").read_text(encoding="utf-8"))
            self.assertEqual("Test User", data_content["name"])
            self.assertEqual("Test bio summary", data_content["bio"])
            self.assertEqual("Test Label", data_content["headline"])
            self.assertIn("test@example.com", data_content["contact_line"])
            self.assertEqual("1 rue Test, 75001 Paris", data_content["address_line"])
            self.assertEqual(1, len(data_content["profiles"]))
            self.assertEqual("LinkedIn", data_content["profiles"][0]["network"])
            self.assertEqual(2, len(data_content["skills"]))
            self.assertIn("Skill 1", data_content["skills"])
            self.assertEqual(1, len(data_content["education"]))
            self.assertEqual("Test University", data_content["education"][0]["institution"])
            self.assertEqual(1, len(data_content["projects"]))
            self.assertEqual("Test Project", data_content["projects"][0]["title"])
            
            # Verify HTML contains the data
            html_content = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Test User", html_content)
            self.assertIn("Test Label", html_content)
            self.assertIn("Test bio summary", html_content)
            self.assertIn("LinkedIn", html_content)
            self.assertIn("Skill 1", html_content)
            self.assertIn("Test University", html_content)
            self.assertIn("Test Project", html_content)

    def test_manual_editor_handles_missing_required_fields(self) -> None:
        """Test that generator handles incomplete data from manual editor gracefully."""
        # Test with missing name
        incomplete_data = {
            "basics": {
                "summary": "Bio without name"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(incomplete_data, output_dir=temp_dir)
            data_content = json.loads((Path(temp_dir) / "data" / "portfolio.json").read_text(encoding="utf-8"))
            # Should still generate with sanitized empty name
            self.assertIsNotNone(data_content["name"])
        
        # Test with missing bio/summary
        incomplete_data2 = {
            "basics": {
                "name": "Test User"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(incomplete_data2, output_dir=temp_dir)
            data_content = json.loads((Path(temp_dir) / "data" / "portfolio.json").read_text(encoding="utf-8"))
            # Should still generate with sanitized empty bio
            self.assertIsNotNone(data_content["bio"])
        
        # Test with empty basics
        incomplete_data3 = {
            "basics": {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_portfolio(incomplete_data3, output_dir=temp_dir)
            self.assertTrue((Path(temp_dir) / "index.html").exists())

    def test_generates_astro_project_structure(self) -> None:
        """Test that Astro portfolio generation creates proper project structure."""
        user_data = {
            "name": "Astro User",
            "bio": "Testing Astro generation",
            "projects": [{"title": "Astro Project", "description": "Test Astro", "image": ""}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_astro_portfolio(user_data, output_dir=temp_dir)
            output = Path(result["path"])
            
            # Check Astro project structure
            self.assertEqual(result["type"], "astro")
            self.assertEqual(result["status"], "generated")
            self.assertIn("npm", result["dev_command"])
            self.assertIn("build", result["build_command"])
            
            # Check Astro files exist
            self.assertTrue((output / "package.json").exists())
            self.assertTrue((output / "astro.config.mjs").exists())
            self.assertTrue((output / ".gitignore").exists())
            self.assertTrue((output / "README.md").exists())
            
            # Check Astro src structure
            self.assertTrue((output / "src" / "layouts" / "Layout.astro").exists())
            self.assertTrue((output / "src" / "pages" / "index.astro").exists())
            self.assertTrue((output / "src" / "content" / "portfolio" / "data.json").exists())
            
            # Check public folder
            self.assertTrue((output / "public" / "styles" / "main.css").exists())
            
            # Verify data content
            data_content = json.loads((output / "src" / "content" / "portfolio" / "data.json").read_text(encoding="utf-8"))
            self.assertEqual("Astro User", data_content["name"])
            self.assertEqual("Testing Astro generation", data_content["bio"])
            self.assertEqual(1, len(data_content["projects"]))
            self.assertEqual("Astro Project", data_content["projects"][0]["title"])
    
    def test_astro_supports_different_templates_and_themes(self) -> None:
        """Test that Astro generation supports different templates and themes."""
        user_data = {
            "basics": {
                "name": "Theme Test",
                "summary": "Testing themes"
            }
        }
        
        # Test with modern theme
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_astro_portfolio(
                user_data,
                output_dir=temp_dir,
                site_template="portfolio",
                design_theme="modern"
            )
            self.assertEqual("modern", result["design_theme"])
            self.assertEqual("portfolio", result["site_template"])
            
            # Check that modern CSS was copied
            output = Path(result["path"])
            css_content = (output / "public" / "styles" / "main.css").read_text(encoding="utf-8")
            self.assertIn("linear-gradient", css_content)  # Modern theme has gradients


if __name__ == "__main__":
    unittest.main()
