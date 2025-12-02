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
TEMPLATE = ROOT / "templates" / "makeup_post_template.html"

# Output directory for per-post pages
POSTS_DIR = ROOT / "makeup" / "posts"


def build_post_html(rows):
    """
    Build HTML body + meta for a single makeup post (list of rows/media).

    For images:
      - Render with <img>.

    For videos (.mp4/.mov/.webm):
      - Render with <video controls> and a poster JPEG:
        expected poster path: same basename as the video but with '.jpg'.
    """
    rep = rows[0]
    caption = (rep.get("caption") or "").strip()
    dt = rep.get("post_datetime") or ""
    subsection = (rep.get("subsection") or "").strip()

    # Meta block (date + subsection if present)
    meta_parts = []
    if dt:
        meta_parts.append(f"<p class='post-date'>{html.escape(dt)}</p>")
    if subsection and subsection.lower() != "general":
        meta_parts.append(
            f"<p class='post-subsection'>{html.escape(subsection.title())}</p>"
        )
    meta_html = "\n".join(meta_parts) if meta_parts else ""

    # Media for this post (images and/or videos)
    media_parts = []
    for row in rows:
        media_path = get_image_path(row)
        if not media_path:
            continue

        # Default alt text
        alt = caption or "Makeup look"
        alt_esc = html.escape(alt, quote=True)

        # Get extension safely
        parts = media_path.lower().rsplit(".", 1)
        ext = parts[-1] if len(parts) == 2 else ""

        if ext in ("mp4", "mov", "webm"):
            # Video: use a poster thumbnail with same base name but .jpg
            base, _ = media_path.rsplit(".", 1)
            poster_path = f"{base}.jpg"

            # Try to pick a reasonable MIME type
            mime_type = {
                "mp4": "video/mp4",
                "mov": "video/quicktime",
                "webm": "video/webm",
            }.get(ext, "video/mp4")

            inner_html = f"""
            <video controls poster="/{poster_path}">
              <source src="/{media_path}" type="{mime_type}">
              Your browser does not support the video tag.
            </video>
            """.rstrip()
        else:
            # Normal image
            inner_html = f'<img src="/{media_path}" alt="{alt_esc}">'

        # Wrap in a figure (consistent for both images and videos)
        media_parts.append(f"""
        <figure class="post-image">
          {inner_html}
        </figure>
        """.rstrip())

    media_html = "\n".join(media_parts)

    # Full caption block
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


def build_makeup_posts():
    rows = load_catalogue()

    # Only makeup posts
    makeup_rows = [
        r for r in rows
        if (r.get("section") or "").lower() == "makeup"
    ]

    if not makeup_rows:
        print("No makeup rows found in catalogue.")
        return

    # Group by post_key
    groups = defaultdict(list)
    for r in makeup_rows:
        key = make_post_key(r)
        groups[key].append(r)

    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    template_text = TEMPLATE.read_text(encoding="utf-8")

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

    print(f"Done. Wrote {count} makeup post pages.")


if __name__ == "__main__":
    build_makeup_posts()
