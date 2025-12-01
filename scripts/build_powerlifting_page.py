# build_powerlifting_page.py
import csv
from pathlib import Path
from textwrap import indent
import html
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
CAPTIONS_INCLUDE = False   # set to True later if you want captions under photos

# Template + output inside the repo
TEMPLATE = ROOT / "templates" / "powerlifting_template.html"
OUTPUT = ROOT / "powerlifting" / "index.html"


def make_gallery_section_for_year(year, items):
    """
    year: string, e.g. "2023"
    items: list of dicts (rows) for that year

    For images:
      - use the image itself as the thumbnail.

    For videos (.mp4/.mov/.webm):
      - use a JPEG poster thumbnail as the thumbnail on the index.
      - expected poster path: same as the video but with '.jpg' extension.

    The thumbnail always links to the per-post page, where the real
    <video> element is rendered.
    """

    figures = []

    # Group rows in this year into posts
    groups = group_rows_by_post(items)

    # Prepare sortable list
    grouped_items = []
    for post_key, rows_for_post in groups.items():
        if not rows_for_post:
            continue
        rep = rows_for_post[0]
        dt = parse_iso_date(rep.get("post_datetime") or "")
        grouped_items.append((post_key, rows_for_post, dt))

    # Newest posts first
    grouped_items.sort(key=lambda t: (t[2] or datetime.min), reverse=True)

    for post_key, rows_for_post, dt in grouped_items:
        rep = rows_for_post[0]

        media_path = get_image_path(rep)
        if not media_path:
            continue

        caption = (rep.get("caption") or "").strip()
        alt_text = caption or "Powerlifting photo"
        alt_esc = html.escape(alt_text, quote=True)

        # Decide thumbnail src
        ext = media_path.lower().rsplit(".", 1)[-1]

        if ext in ("mp4", "mov", "webm"):
            # Use a poster image with the same base name but .jpg
            base, _ = media_path.rsplit(".", 1)
            thumb_path = f"{base}.jpg"
        else:
            # Normal image file as-is
            thumb_path = media_path

        thumb_src = f"/{thumb_path}"

        # Link to per-post powerlifting page
        slug = make_post_slug(rep)
        href = f"/powerlifting/posts/{slug}.html"

        if CAPTIONS_INCLUDE:
            caption_html = f"<figcaption>{html.escape(caption)}</figcaption>"
        else:
            caption_html = ""

        fig_html = f"""
        <figure class="gallery-item">
          <a href="{href}">
            <img src="{thumb_src}" alt="{alt_esc}">
          </a>
          {caption_html}
        </figure>
        """.rstrip()

        figures.append(fig_html)

    if not figures:
        return ""

    figures_html = "\n\n".join(figures)
    section_title = year if year else "Unsorted"

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


def build_powerlifting_page():
    rows = load_catalogue()

    # Filter for powerlifting only
    pl_rows = [
        r for r in rows
        if (r.get("section") or "").lower() == "powerlifting"
    ]

    # Group rows by subsection (year)
    by_year = {}
    for r in pl_rows:
        year = (r.get("subsection") or "").strip()
        if not year:
            year = ""  # bucket for unknown
        by_year.setdefault(year, []).append(r)

    # Sort years descending, but put "" (unknown) at the end
    years = sorted(
        [y for y in by_year.keys() if y],
        reverse=True
    )
    if "" in by_year:
        years.append("")  # unknown at end

    sections_html = []
    for year in years:
        items = by_year[year]
        section_html = make_gallery_section_for_year(year, items)
        if section_html:
            sections_html.append(section_html)

    galleries_html = "\n\n".join(sections_html) if sections_html else "<p>No powerlifting photos yet.</p>"

    template_text = TEMPLATE.read_text(encoding="utf-8")
    final_html = template_text.replace("{{GALLERIES}}", galleries_html)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(final_html, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_powerlifting_page()
