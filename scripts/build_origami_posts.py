import csv
import re
from pathlib import Path
from collections import defaultdict
import html

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

 
# Template file
TEMPLATE = ROOT / "templates" / "origami_post_template.html"

# Output directory for per-post pages
POSTS_DIR = ROOT / "origami" / "posts"
 

def build_post_html(rows):
    """
    Build HTML body + meta for a single post (list of rows/media).
    Supports both images and videos (mp4/mov/webm).
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

    # media (images / videos) for this post
    media_parts = []
    for row in rows:
        media_path = get_image_path(row)
        if not media_path:
            continue

        alt = caption or "Origami model"
        alt_esc = html.escape(alt, quote=True)

        ext = media_path.lower().split(".")[-1]

        # Video?
        if ext in ("mp4", "mov", "webm"):
            media_html = f"""
            <video controls preload="metadata">
              <source src="/{media_path}" type="video/{ext}">
              Your browser does not support the video tag.
            </video>
            """.strip()
        else:
            media_html = f'<img src="/{media_path}" alt="{alt_esc}">'

        media_parts.append(f'<figure class="post-image">{media_html}</figure>')

    media_html = "\n".join(media_parts)

    # full caption
    if caption:
        caption_html = f"<div class='post-caption'><p>{html.escape(caption)}</p></div>"
    else:
        caption_html = ""

    body_html = f"""
    <article class="post-detail">
      {media_html}
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
