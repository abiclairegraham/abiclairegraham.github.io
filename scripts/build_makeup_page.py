import csv
from pathlib import Path
from textwrap import indent
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


# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # set to True later if you want captions under photos

# Template + output inside the repo
TEMPLATE = ROOT / "templates" / "makeup_template.html"
OUTPUT = ROOT / "makeup" / "index.html"


def make_gallery_section(title, items, show_heading=True):
    """
    If show_heading=False, we omit the <h2> so it feels like 'just a gallery'.

    For images:
      - use the image itself as the thumbnail.

    For videos (.mp4/.mov/.webm):
      - use a JPEG poster thumbnail as the thumbnail on the index.
      - expected poster path: same as the video but with '.jpg' extension.

    The thumbnail always links to the per-post page, where the real
    <img> or <video> element is rendered.
    """
    figures = []

    for item in items:
        media_path = get_image_path(item)
        if not media_path:
            continue

        caption = (item.get("caption") or "").strip()
        alt_text = caption or "Makeup look"
        alt_text_esc = html.escape(alt_text, quote=True)

        # Decide thumbnail src based on extension
        # (be defensive if there's no dot)
        parts = media_path.lower().rsplit(".", 1)
        ext = parts[-1] if len(parts) == 2 else ""

        is_video = ext in ("mp4", "mov", "webm")
        if is_video:
            # Use a poster image with the same base name but .jpg
            base, _ = media_path.rsplit(".", 1)
            thumb_path = f"{base}.jpg"
        else:
            # Normal image file as-is
            thumb_path = media_path

        thumb_src = f"/{thumb_path}"

        # Link to the corresponding per-post makeup page
        slug = make_post_slug(item)
        href = f"/makeup/posts/{slug}.html"

        # Optional figcaption under thumbnail
        if CAPTIONS_INCLUDE:
            caption_esc = html.escape(caption)
            caption_html = f"<figcaption>{caption_esc}</figcaption>"
        else:
            caption_html = ""

        # Optional: tiny "video" badge overlay if it's a video
        video_badge_html = '<span class="video-badge">▶</span>' if is_video else ""

        fig_html = f"""
        <figure class="gallery-item">
          <a href="{href}">
            <div class="thumb-wrapper">
              <img src="{thumb_src}" alt="{alt_text_esc}">
              {video_badge_html}
            </div>
          </a>
          {caption_html}
        </figure>
        """.rstrip()

        figures.append(fig_html)

    if not figures:
        return ""

    figures_html = "\n\n".join(figures)

    if show_heading:
        heading_html = f"<h2>{html.escape(title)}</h2>"
    else:
        heading_html = ""

    section_html = f"""
    <section class="gallery">
      {heading_html}
      <div class="gallery-grid">
{indent(figures_html, "        ")}
      </div>
    </section>
    """.rstrip()

    return section_html


def build_makeup_page():
    rows = load_catalogue()

    # Filter for makeup only
    mk_rows = [
        r for r in rows
        if (r.get("section") or "").lower() == "makeup"
    ]

    if not mk_rows:
        galleries_html = "<p>No makeup looks yet.</p>"
    else:
        # Collect non-empty subsections
        subsections = sorted({
            (r.get("subsection") or "").strip()
            for r in mk_rows
            if (r.get("subsection") or "").strip()
        })

        # If no subsections at all -> one big gallery, no subsection headings
        if not subsections:
            galleries_html = make_gallery_section(
                title="",
                items=mk_rows,
                show_heading=False,
            )
        else:
            # Group by subsection and build one section per group
            sections_html = []
            for sub in subsections:
                items = [
                    r for r in mk_rows
                    if (r.get("subsection") or "").strip() == sub
                ]
                if not items:
                    continue
                # Nice title-cased heading for the subsection
                title = sub.strip().title()
                section_html = make_gallery_section(
                    title=title,
                    items=items,
                    show_heading=True,
                )
                if section_html:
                    sections_html.append(section_html)

            galleries_html = "\n\n".join(sections_html) if sections_html else "<p>No makeup looks yet.</p>"

    template_text = TEMPLATE.read_text(encoding="utf-8")
    final_html = template_text.replace("{{GALLERIES}}", galleries_html)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(final_html, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_makeup_page()
