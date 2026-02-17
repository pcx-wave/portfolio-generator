import json
import tempfile
import unittest
from pathlib import Path

from generate_portfolio import generate_portfolio


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

            html_content = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Alice &lt;Dev&gt;", html_content)

            data_content = json.loads((output / "data" / "portfolio.json").read_text(encoding="utf-8"))
            self.assertEqual("Alice &lt;Dev&gt;", data_content["name"])


if __name__ == "__main__":
    unittest.main()
