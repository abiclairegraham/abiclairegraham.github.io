import csv
from pathlib import Path
from textwrap import indent
import html
import re
from collections import defaultdict
from datetime import datetime

from scripts.build_common import (
    ROOT,
    CATALOGUE_PATH,
    load_catalogue,
    get_image_path,
    slugify,
    make_post_slug,
    make_post_key,
    group_rows_by_post,
    parse_iso_date,
)

# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # <<< change to True if you want captions later
 
# Template + output inside the repo
TEMPLATE = ROOT / "templates" / "origami_template.html"
OUTPUT = ROOT / "origami" / "index.html"

ORIGAMI_SUBSECTIONS = [
    ("insects", "Insects"),
    ("animals", "Animals"),
    ("tessellations", "Tessellations"),
    ("curved", "Curved Origami"),
    ("modular", "Modular Origami"),
    ("general", "General"),
]


# --------------------------------------
# Helpers
# --------------------------------------


def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

 
def make_gallery_section(title, post_groups):
    """
    post_groups: list of (post_key, [rows_for_post])
    Returns HTML for one section.
    """
    figures = []

    for post_key, items in post_groups:
        if not items:
            continue

        # representative row for this post (first item)
        rep = items[0]
        img_path = get_image_path(rep)
        if not img_path:
            continue

        caption = (rep.get("caption") or "").strip()
        alt_text = caption or "Origami model"
        alt_text_esc = html.escape(alt_text, quote=True)

        # link to the corresponding post page
        slug = make_post_slug(rep)
        href = f"/origami/posts/{slug}.html"

        # Optional figcaption under thumbnail
        if CAPTIONS_INCLUDE:
            caption_esc = html.escape(caption)
            caption_html = f"<figcaption>{caption_esc}</figcaption>"
        else:
            caption_html = ""

        fig_html = f"""
        <figure class="gallery-item">
          <a href="{href}">
            <img src="/{img_path}" alt="{alt_text_esc}">
          </a>
          {caption_html}
        </figure>
        """.rstrip()

        figures.append(fig_html)

    if not figures:
        return ""

    figures_html = "\n\n".join(figures)

    section_html = f"""
    <section class="gallery">
        <div class="mini-plaque">
         <div class="mini-plaque-inner">
          <h2>{html.escape(title)}</h2>
         </div>
        </div>
      <div class="gallery-grid">
{indent(figures_html, "        ")}
      </div>
    </section>

    """.rstrip()

    return section_html


def build_origami_page():
    rows = load_catalogue()
    # Only origami rows
    origami_rows = [r for r in rows if (r.get("section") or "").lower() == "origami"]

    if not origami_rows:
        galleries_html = "<p>No origami yet.</p>"
    else:
        sections_html = []

        for key, title in ORIGAMI_SUBSECTIONS:
            # rows that belong to this subsection
            rows_for_sub = [
                r for r in origami_rows
                if (r.get("subsection") or "").lower() == key
            ]
            if not rows_for_sub:
                continue

            # group into posts
            groups = group_rows_by_post(rows_for_sub)

            # sort posts by newest date (using representative row)
            grouped_items = []
            for post_key, items in groups.items():
                rep = items[0]
                dt = parse_dt(rep.get("post_datetime") or "")
                grouped_items.append((post_key, items, dt))

            grouped_items.sort(key=lambda t: (t[2] or datetime.min), reverse=True)

            # drop the datetime from the tuple for HTML generation
            section_html = make_gallery_section(
                title,
                [(pk, items) for (pk, items, _dt) in grouped_items]
            )

            if section_html:
                sections_html.append(section_html)

        galleries_html = "\n\n".join(sections_html) if sections_html else "<p>No origami yet.</p>"

    template_text = TEMPLATE.read_text(encoding="utf-8")
    final_html = template_text.replace("{{GALLERIES}}", galleries_html)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(final_html, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_origami_page()
