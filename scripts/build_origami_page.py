import csv
from pathlib import Path
from textwrap import indent
import html
import re
from collections import defaultdict
from datetime import datetime

# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # <<< change to True if you want captions later

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Catalogue path in Drive (adjust if needed)
# CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv")
CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_labeled.csv")

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

def load_catalogue():
    rows = []
    with CATALOGUE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_image_path(row):
    """Use filename_relative if present, else fallback to filename_raw."""
    if "filename_relative" in row and row["filename_relative"]:
        return row["filename_relative"].lstrip("/")
    if "filename_raw" in row and row["filename_raw"]:
        return row["filename_raw"].lstrip("/")
    return ""


def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def make_post_key(row):
    """
    Build a grouping key for 'posts' from existing columns.
    Using (source, post_datetime, json_source) should uniquely
    identify an Instagram post in your export.
    """
    source = row.get("source", "") or "instagram"
    dt = row.get("post_datetime", "") or ""
    js = row.get("json_source", "") or ""
    return f"{source}::{dt}::{js}"

def slugify(text, max_len=80):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "post"


def make_post_slug(row: dict) -> str:
    """
    Get slug for this post from the CSV.
    If 'post_slug' is missing/empty, fall back to a deterministic slug
    based on post_datetime + post_key.
    """
    slug = (row.get("post_slug") or "").strip()
    if slug:
        # If you've already slugified in the CSV, you *could* just return slug.
        # Keeping slugify here is a light safety net in case there are spaces etc.
        return slugify(slug)

    # Fallback: derive from section/date/post_key
    section = (row.get("section") or "origami").lower()
    dt = row.get("post_datetime", "") or ""
    date_part = dt[:10] if len(dt) >= 10 else "unknown-date"

    source = row.get("source", "") or "instagram"
    js = row.get("json_source", "") or ""
    post_key = f"{source}::{dt}::{js}"

    base = f"{section}-{date_part}-{post_key}"
    return slugify(base)


def group_rows_by_post(rows):
    """Group a list of rows into {post_key: [rows...]}."""
    groups = defaultdict(list)
    for r in rows:
        key = make_post_key(r)
        groups[key].append(r)
    return groups


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
      <h2>{html.escape(title)}</h2>
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
