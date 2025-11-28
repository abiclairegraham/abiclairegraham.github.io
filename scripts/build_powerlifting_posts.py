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

# Template file for powerlifting posts
TEMPLATE = ROOT / "templates" / "powerlifting_post_template.html"

# Output directory for per-post pages
POSTS_DIR = ROOT / "powerlifting" / "posts"


def build_post_html(rows):
    """
    Build HTML body + meta for a single powerlifting post (list of rows/images).
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
        alt = caption or "Powerlifting photo"
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


def build_powerlifting_posts():
    rows = load_catalogue()

    # Only powerlifting posts
    pl_rows = [
        r for r in rows
        if (r.get("section") or "").lower() == "powerlifting"
    ]

    if not pl_rows:
        print("No powerlifting rows found in catalogue.")
        return

    # Group by post_key
    groups = defaultdict(list)
    for r in pl_rows:
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

    print(f"Done. Wrote {count} powerlifting post pages.")


if __name__ == "__main__":
    build_powerlifting_posts()
