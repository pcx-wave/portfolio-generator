import argparse
from datetime import datetime, timezone
import html
import json
import re
import shutil
from uuid import uuid4
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


def _cv_to_portfolio_payload(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    basics = cv_data.get("basics") or {}
    mapped_projects: List[Dict[str, str]] = []

    for project in cv_data.get("projects") or []:
        mapped_projects.append(
            {
                "title": project.get("name", ""),
                "description": project.get("description", ""),
                "image": project.get("image", ""),
            }
        )

    for work in cv_data.get("work") or []:
        highlights_value = work.get("highlights")
        highlights_list = highlights_value if isinstance(highlights_value, list) else []
        highlights = ", ".join(str(item) for item in highlights_list)
        description = " ".join([work.get("summary", ""), highlights]).strip()
        mapped_projects.append(
            {
                "title": " - ".join(filter(None, [work.get("position"), work.get("name")])),
                "description": description,
                "image": "",
            }
        )

    return {
        "user_id": cv_data.get("user_id") or basics.get("email"),
        "name": basics.get("name"),
        "bio": basics.get("summary") or basics.get("label"),
        "projects": mapped_projects,
    }


def normalize_input_payload(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Support legacy portfolio payload and CV augmented/JSON Resume-like payload."""
    if "basics" in user_data:
        return _cv_to_portfolio_payload(user_data)
    return user_data


def build_portfolio_record(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a canonical MongoDB-friendly record with SQL-friendly identifiers."""
    normalized_payload = normalize_input_payload(user_data)
    now = datetime.now(timezone.utc).isoformat()
    raw_user_id = normalized_payload.get("user_id")
    user_id = _sanitize_text(raw_user_id) if raw_user_id is not None else ""
    if not user_id:
        user_id = str(uuid4())
    projects: List[Dict[str, Any]] = []
    for project in _normalize_projects(normalized_payload.get("projects")):
        projects.append(
            {
                "project_id": str(uuid4()),
                "title": project["title"],
                "description": project["description"],
                "image": project["image"],
            }
        )
    return {
        "portfolio_id": str(uuid4()),
        "user_id": user_id,
        "name": _sanitize_text(normalized_payload.get("name")),
        "bio": _sanitize_text(normalized_payload.get("bio")),
        "projects": projects,
        "created_at": now,
        "updated_at": now,
    }


def _build_sql_projection(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "portfolios": [
            {
                "portfolio_id": record["portfolio_id"],
                "user_id": record["user_id"],
                "name": record["name"],
                "bio": record["bio"],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"],
            }
        ],
        "projects": [
            {
                "project_id": project["project_id"],
                "portfolio_id": record["portfolio_id"],
                "title": project["title"],
                "description": project["description"],
                "image": project["image"],
            }
            for project in record["projects"]
        ],
    }


def generate_portfolio(
    user_data: Dict[str, Any], output_dir: str = "dist", mongo_collection: Any = None
) -> Dict[str, str]:
    """Generate a static portfolio that can be deployed directly on Netlify."""
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / "index.html"
    css_path = base_dir / "templates" / "styles" / "main.css"
    output_path = Path(output_dir).resolve()

    record = build_portfolio_record(user_data)
    name = record["name"]
    bio = record["bio"]
    projects = record["projects"]

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
    (output_path / "data" / "portfolio_document.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "data" / "portfolio_sql_projection.json").write_text(
        json.dumps(_build_sql_projection(record), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "netlify.toml").write_text(NETLIFY_TOML, encoding="utf-8")

    response = {"path": str(output_path), "admin_url": "/admin/", "portfolio_id": record["portfolio_id"]}
    if mongo_collection is not None:
        try:
            mongo_collection.insert_one(record)
            response["storage"] = "mongodb"
        except Exception as error:  # pragma: no cover - depends on runtime DB availability
            response["storage"] = "mongodb_error"
            response["storage_error"] = str(error)
    return response


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
