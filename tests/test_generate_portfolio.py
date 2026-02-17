import json
import tempfile
import unittest
from pathlib import Path

from generate_portfolio import generate_portfolio, mark_site_validated


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

    def test_accepts_cv_augmented_input_format(self) -> None:
        cv_data = {
            "basics": {"name": "Marie Curie", "summary": "Data scientist"},
            "work": [
                {
                    "name": "LabX",
                    "position": "ML Engineer",
                    "summary": "Built ranking models",
                    "highlights": ["Improved precision", "Reduced latency"],
                }
            ],
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


if __name__ == "__main__":
    unittest.main()
