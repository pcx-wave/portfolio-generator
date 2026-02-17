import argparse
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_PROJECT_IMAGE = "https://via.placeholder.com/400x250/0077b6/FFFFFF?text=Project"
PROJECT_CARD_TEMPLATE = """                <div class="project-card">
                    <img src="{image}" alt="{title}">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>"""

DECAP_ADMIN_INDEX = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Portfolio Content Manager</title>
  </head>
  <body>
    <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
  </body>
</html>
"""

DECAP_CONFIG_YML = """backend:
  name: git-gateway
  branch: main
media_folder: "images/uploads"
public_folder: "/images/uploads"
collections:
  - name: "portfolio"
    label: "Portfolio"
    files:
      - label: "Profile"
        name: "profile"
        file: "data/portfolio.json"
        format: "json"
        fields:
          - {{ label: "Name", name: "name", widget: "string" }}
          - {{ label: "Bio", name: "bio", widget: "text" }}
          - label: "Projects"
            name: "projects"
            widget: "list"
            fields:
              - {{ label: "Title", name: "title", widget: "string" }}
              - {{ label: "Description", name: "description", widget: "text" }}
              - {{ label: "Image", name: "image", widget: "string", required: false }}
"""

NETLIFY_TOML = """[build]
  publish = "."
"""


def _sanitize_text(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _normalize_projects(projects: Any) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for project in projects or []:
        normalized.append(
            {
                "title": _sanitize_text(project.get("title")),
                "description": _sanitize_text(project.get("description")),
                "image": _sanitize_text(project.get("image") or DEFAULT_PROJECT_IMAGE),
            }
        )
    return normalized


def generate_portfolio(user_data: Dict[str, Any], output_dir: str = "dist") -> Dict[str, str]:
    """Generate a static portfolio that can be deployed directly on Netlify."""
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / "index.html"
    css_path = base_dir / "templates" / "styles" / "main.css"
    output_path = Path(output_dir).resolve()

    name = _sanitize_text(user_data.get("name"))
    bio = _sanitize_text(user_data.get("bio"))
    projects = _normalize_projects(user_data.get("projects"))

    html_template = template_path.read_text(encoding="utf-8")
    cards = "\n".join(
        PROJECT_CARD_TEMPLATE.format(
            image=project["image"],
            title=project["title"],
            description=project["description"],
        )
        for project in projects
    )
    rendered_html = html_template.replace("{{name}}", name).replace("{{bio}}", bio)
    rendered_html, replaced = re.subn(
        r"\s*\{%\s*for project in projects\s*%\}.*?\{%\s*endfor\s*%\}",
        f"\n{cards}",
        rendered_html,
        flags=re.DOTALL,
    )
    if replaced != 1:
        raise ValueError(
            "Template project loop block ({% for project in projects %}...{% endfor %}) not found or appears multiple times in template"
        )

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "styles").mkdir(parents=True, exist_ok=True)
    (output_path / "admin").mkdir(parents=True, exist_ok=True)
    (output_path / "data").mkdir(parents=True, exist_ok=True)

    (output_path / "index.html").write_text(rendered_html, encoding="utf-8")
    shutil.copy2(css_path, output_path / "styles" / "main.css")
    (output_path / "admin" / "index.html").write_text(DECAP_ADMIN_INDEX, encoding="utf-8")
    (output_path / "admin" / "config.yml").write_text(DECAP_CONFIG_YML, encoding="utf-8")
    (output_path / "data" / "portfolio.json").write_text(
        json.dumps({"name": name, "bio": bio, "projects": projects}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "netlify.toml").write_text(NETLIFY_TOML, encoding="utf-8")

    return {"path": str(output_path), "admin_url": "/admin/"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static portfolio from a JSON payload.")
    parser.add_argument("--input", required=True, help="Path to a JSON file containing name, bio and projects")
    parser.add_argument("--output-dir", default="dist", help="Output directory for generated static site")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = generate_portfolio(payload, output_dir=args.output_dir)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
