import csv
import re
from pathlib import Path
from collections import defaultdict
import html

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Catalogue path in Drive (adjust if needed)
CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_labeled.csv")

# Template file
TEMPLATE = ROOT / "templates" / "origami_post_template.html"

# Output directory for per-post pages
POSTS_DIR = ROOT / "origami" / "posts"


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



def build_post_html(rows):
    """
    Build HTML body + meta for a single post (list of rows/images).
    """
    rep = rows[0]
    caption = (rep.get("caption") or "").strip()
    dt = rep.get("post_datetime") or ""
    subsection = (rep.get("subsection") or "").strip()

    # meta block (date + subsection if present)
    meta_parts = []
    if dt:
        meta_parts.append(f"<p class='post-date'>{html.escape(dt)}</p>")
    if subsection and subsection != "general":
        meta_parts.append(f"<p class='post-subsection'>{html.escape(subsection.title())}</p>")
    meta_html = "\n".join(meta_parts) if meta_parts else ""

    # images for this post
    image_parts = []
    for row in rows:
        img_path = get_image_path(row)
        if not img_path:
            continue
        alt = caption or "Origami model"
        alt_esc = html.escape(alt, quote=True)
        image_parts.append(
            f'<figure class="post-image"><img src="/{img_path}" alt="{alt_esc}"></figure>'
        )

    images_html = "\n".join(image_parts)

    # full caption
    if caption:
        caption_html = f"<div class='post-caption'><p>{html.escape(caption)}</p></div>"
    else:
        caption_html = ""

    body_html = f"""
    <article class="post-detail">
      {images_html}
      {caption_html}
    </article>
    """.rstrip()

    return meta_html, body_html


def build_origami_posts():
    rows = load_catalogue()

    # Only origami posts
    origami_rows = [
        r for r in rows
        if (r.get("section") or "").lower() == "origami"
    ]

    if not origami_rows:
        print("No origami rows found in catalogue.")
        return

    # Group by post_key
    groups = defaultdict(list)
    for r in origami_rows:
        key = make_post_key(r)
        groups[key].append(r)

    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    template_text = TEMPLATE.read_text(encoding="utf-8")

    used_slugs = set()
    count = 0

    for key, group_rows in groups.items():
        rep = group_rows[0]
        slug = make_post_slug(rep)
        out_path = POSTS_DIR / f"{slug}.html"

        meta_html, body_html = build_post_html(group_rows)

        html_text = (
            template_text
            .replace("{{META}}", meta_html)
            .replace("{{BODY}}", body_html)
        )

        out_path.write_text(html_text, encoding="utf-8")
        count += 1
        print("Wrote", out_path)

    print(f"Done. Wrote {count} origami post pages.")


if __name__ == "__main__":
    build_origami_posts()
