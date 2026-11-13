import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .config import config
from .db import get_all_papers


def generate_html_page(db_path: str, output_dir: str, template_path: str = None) -> str:
    if template_path is None:
        template_path = config.template_path

    os.makedirs(output_dir, exist_ok=True)
    raw_papers = get_all_papers(db_path)

    formatted_papers = []
    for p in raw_papers:
        kw = p.get("keywords") or []
        if isinstance(kw, list):
            kw_display = ", ".join(kw)
        else:
            kw_display = str(kw)

        proc_at = str(p.get("processed_at", "")).split(".")[0]

        formatted_papers.append(
            {
                "title": p.get("title", "Sans titre"),
                "category": p.get("category", "Non classe"),
                "summary": p.get("summary", ""),
                "keywords": kw,
                "keywords_display": kw_display,
                "filename": p.get("filename", ""),
                "processed_at_display": proc_at,
            }
        )

    template_dir = os.path.dirname(os.path.abspath(template_path))
    template_name = os.path.basename(template_path)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)
    rendered_html = template.render(papers=formatted_papers)

    output_file = os.path.join(output_dir, "index.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return output_file
