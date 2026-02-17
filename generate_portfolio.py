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
DEFAULT_PROFILE_PHOTO = "https://via.placeholder.com/240x240/2c3e50/FFFFFF?text=Profile"
DEFAULT_TEMPLATE_MODE = "hybrid"
DEFAULT_DESIGN_THEME = "classic"
TEMPLATE_MODES = {"portfolio", "cv", "hybrid"}
DESIGN_THEME_FILES = {"classic": "main.css", "modern": "modern.css", "contrast": "contrast.css", "artistic": "artistic.css"}
SECTION_TITLE_BY_TEMPLATE = {"portfolio": "Réalisations", "cv": "Expériences", "hybrid": "Réalisations & Expériences"}
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


def _normalize_profiles(profiles: Any) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for profile in profiles or []:
        network = _sanitize_text(profile.get("network"))
        url = _sanitize_text(profile.get("url") or profile.get("username"))
        if network or url:
            normalized.append({"network": network or "Profil", "url": url})
    return normalized


def _normalize_skills(skills: Any) -> List[str]:
    normalized: List[str] = []
    for skill in skills or []:
        name = _sanitize_text(skill.get("name"))
        if name:
            normalized.append(name)
        for keyword in skill.get("keywords") or []:
            normalized.append(_sanitize_text(keyword))
    return [value for value in normalized if value]


def _normalize_education(education: Any) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for item in education or []:
        title = " - ".join(
            filter(None, [_sanitize_text(item.get("studyType")), _sanitize_text(item.get("area"))])
        )
        period = " → ".join(filter(None, [_sanitize_text(item.get("startDate")), _sanitize_text(item.get("endDate"))]))
        normalized.append(
            {
                "institution": _sanitize_text(item.get("institution")),
                "title": title,
                "period": period,
                "score": _sanitize_text(item.get("score")),
            }
        )
    return normalized


def _cv_to_portfolio_payload(cv_data: Dict[str, Any], site_template: str = DEFAULT_TEMPLATE_MODE) -> Dict[str, Any]:
    basics = cv_data.get("basics") or {}
    location = basics.get("location") or {}
    mapped_projects: List[Dict[str, str]] = []

    for project in cv_data.get("projects") or []:
        mapped_projects.append(
            {
                "title": project.get("name", ""),
                "description": project.get("description", ""),
                "image": project.get("image", ""),
            }
        )

    work_projects: List[Dict[str, str]] = []
    for work in cv_data.get("work") or []:
        highlights_value = work.get("highlights")
        highlights_list = highlights_value if isinstance(highlights_value, list) else []
        highlights = ", ".join(str(item) for item in highlights_list)
        description = " ".join([work.get("summary", ""), highlights]).strip()
        work_projects.append(
            {
                "title": " - ".join(filter(None, [work.get("position"), work.get("name")])),
                "description": description,
                "image": "",
            }
        )

    if site_template == "portfolio":
        selected_projects = mapped_projects
    elif site_template == "cv":
        selected_projects = work_projects
    elif site_template == "hybrid":
        selected_projects = mapped_projects + work_projects
    else:
        raise ValueError(f"Unsupported site_template '{site_template}'")

    return {
        "user_id": cv_data.get("user_id") or basics.get("email"),
        "name": basics.get("name"),
        "bio": basics.get("summary") or basics.get("label"),
        "headline": basics.get("label"),
        "photo_url": basics.get("image"),
        "email": basics.get("email"),
        "phone": basics.get("phone"),
        "address_line": " | ".join(
            filter(
                None,
                [
                    location.get("address"),
                    " ".join(filter(None, [location.get("postalCode"), location.get("city")])),
                    location.get("region"),
                    location.get("countryCode"),
                ],
            )
        ),
        "profiles": basics.get("profiles") or [],
        "skills": cv_data.get("skills") or [],
        "education": cv_data.get("education") or [],
        "projects": selected_projects,
    }


def normalize_input_payload(user_data: Dict[str, Any], site_template: str = DEFAULT_TEMPLATE_MODE) -> Dict[str, Any]:
    """Support legacy portfolio payload and CV augmented/JSON Resume-like payload."""
    if "basics" in user_data:
        return _cv_to_portfolio_payload(user_data, site_template=site_template)
    return user_data


def build_portfolio_record(user_data: Dict[str, Any], site_template: str = DEFAULT_TEMPLATE_MODE) -> Dict[str, Any]:
    """Build a canonical MongoDB-friendly record with SQL-friendly identifiers."""
    if site_template not in TEMPLATE_MODES:
        raise ValueError(f"Unsupported site_template '{site_template}'. Expected one of: {sorted(TEMPLATE_MODES)}")
    normalized_payload = normalize_input_payload(user_data, site_template=site_template)
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
        "headline": _sanitize_text(normalized_payload.get("headline") or "Profil professionnel"),
        "photo_url": _sanitize_text(normalized_payload.get("photo_url") or DEFAULT_PROFILE_PHOTO),
        "contact_line": (
            " | ".join(
                filter(
                    None,
                    [
                        _sanitize_text(normalized_payload.get("email")),
                        _sanitize_text(normalized_payload.get("phone")),
                    ],
                )
            )
            or "Contact non renseigné"
        ),
        "address_line": _sanitize_text(normalized_payload.get("address_line") or "Adresse non renseignée"),
        "profiles": _normalize_profiles(normalized_payload.get("profiles")),
        "skills": _normalize_skills(normalized_payload.get("skills")),
        "education": _normalize_education(normalized_payload.get("education")),
        "projects": projects,
        "created_at": now,
        "updated_at": now,
        "site_template": site_template,
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


def mark_site_validated(output_dir: str) -> Dict[str, str]:
    output_path = Path(output_dir).resolve()
    workflow_state_path = output_path / "data" / "workflow_state.json"
    try:
        state = json.loads(workflow_state_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Cannot validate site at '{output_path}': missing or invalid data/workflow_state.json. Generate a draft first."
        ) from error
    state["status"] = "validated"
    state["validated_at"] = datetime.now(timezone.utc).isoformat()
    workflow_state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"path": str(output_path), "status": "validated"}


def generate_portfolio(
    user_data: Dict[str, Any],
    output_dir: str = "dist",
    mongo_collection: Any = None,
    site_template: str = DEFAULT_TEMPLATE_MODE,
    design_theme: str = DEFAULT_DESIGN_THEME,
) -> Dict[str, str]:
    """Generate a static portfolio that can be deployed directly on Netlify."""
    if site_template not in TEMPLATE_MODES:
        raise ValueError(f"Unsupported site_template '{site_template}'. Expected one of: {sorted(TEMPLATE_MODES)}")
    if design_theme not in DESIGN_THEME_FILES:
        raise ValueError(f"Unsupported design_theme '{design_theme}'. Expected one of: {sorted(DESIGN_THEME_FILES)}")
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / "index.html"
    css_path = base_dir / "templates" / "styles" / DESIGN_THEME_FILES[design_theme]
    output_path = Path(output_dir).resolve()

    record = build_portfolio_record(user_data, site_template=site_template)
    name = record["name"]
    bio = record["bio"]
    projects = record["projects"]
    profiles_html = "\n".join(
        f'<li><strong>{profile["network"]}</strong> : <a href="{profile["url"]}">{profile["url"]}</a></li>'
        for profile in record["profiles"]
    ) or "<li>Non renseigné</li>"
    skills_html = "\n".join(f'<span class="skill-tag">{skill}</span>' for skill in record["skills"]) or "<span>Aucune</span>"
    education_html = "\n".join(
        (
            '<div class="education-item">'
            f"<h3>{item['institution']}</h3>"
            f"<p>{item['title']}</p>"
            f"<p>{item['period']}</p>"
            f"<p>{item['score']}</p>"
            "</div>"
        )
        for item in record["education"]
    ) or '<div class="education-item"><h3>Formation non renseignée</h3></div>'

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
    rendered_html = rendered_html.replace("{{section_title}}", SECTION_TITLE_BY_TEMPLATE[site_template])
    rendered_html = rendered_html.replace("{{photo_url}}", record["photo_url"])
    rendered_html = rendered_html.replace("{{headline}}", record["headline"])
    rendered_html = rendered_html.replace("{{contact_line}}", record["contact_line"])
    rendered_html = rendered_html.replace("{{address_line}}", record["address_line"])
    rendered_html = rendered_html.replace("{{profiles_html}}", profiles_html)
    rendered_html = rendered_html.replace("{{skills_html}}", skills_html)
    rendered_html = rendered_html.replace("{{education_html}}", education_html)
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
        json.dumps(
            {
                "name": name,
                "bio": bio,
                "headline": record["headline"],
                "photo_url": record["photo_url"],
                "contact_line": record["contact_line"],
                "address_line": record["address_line"],
                "profiles": record["profiles"],
                "skills": record["skills"],
                "education": record["education"],
                "projects": projects,
            },
            ensure_ascii=False,
            indent=2,
        ),
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
    (output_path / "data" / "workflow_state.json").write_text(
        json.dumps(
            {
                "status": "draft",
                "site_template": site_template,
                "portfolio_id": record["portfolio_id"],
                "editable_admin_url": "/admin/",
                "design_theme": design_theme,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_path / "netlify.toml").write_text(NETLIFY_TOML, encoding="utf-8")

    response = {
        "path": str(output_path),
        "admin_url": "/admin/",
        "portfolio_id": record["portfolio_id"],
        "site_template": site_template,
        "design_theme": design_theme,
        "status": "draft",
    }
    if mongo_collection is not None:
        try:
            mongo_collection.insert_one(record)
            response["storage"] = "mongodb"
        except Exception as error:  # pragma: no cover - depends on runtime DB availability
            response["storage"] = "mongodb_error"
            response["storage_error"] = str(error)
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or validate a static portfolio site from a JSON payload.")
    parser.add_argument("--input", help="Path to a JSON file containing portfolio or CV input data")
    parser.add_argument("--output-dir", default="dist", help="Output directory for generated static site")
    parser.add_argument(
        "--site-template",
        choices=sorted(TEMPLATE_MODES),
        default=DEFAULT_TEMPLATE_MODE,
        help="Template mode to generate: portfolio, cv, or hybrid",
    )
    parser.add_argument(
        "--design-theme",
        choices=sorted(DESIGN_THEME_FILES),
        default=DEFAULT_DESIGN_THEME,
        help="Design theme to generate: classic, modern, contrast, or artistic",
    )
    parser.add_argument("--validate", action="store_true", help="Mark an existing generated draft as validated")
    args = parser.parse_args()

    if args.validate:
        result = mark_site_validated(args.output_dir)
    else:
        if not args.input:
            raise ValueError("--input is required unless --validate is used")
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = generate_portfolio(
            payload,
            output_dir=args.output_dir,
            site_template=args.site_template,
            design_theme=args.design_theme,
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
