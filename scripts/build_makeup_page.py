import csv
from pathlib import Path
from textwrap import indent
import html

# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # set to True later if you want captions under photos

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Catalogue path in Drive (adjust if needed)
CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv")

# Template + output inside the repo
TEMPLATE = ROOT / "templates" / "makeup_template.html"
OUTPUT = ROOT / "makeup" / "index.html"


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


def make_gallery_section(title, items, show_heading=True):
    """
    If show_heading=False, we omit the <h2> so it feels like 'just a gallery'.
    """
    figures = []

    for item in items:
        img_path = get_image_path(item)
        if not img_path:
            continue

        caption = (item.get("caption") or "").strip()
        alt_text = caption or "Makeup look"

        alt_text_esc = html.escape(alt_text, quote=True)

        if CAPTIONS_INCLUDE:
            caption_esc = html.escape(caption)
            caption_html = f"<figcaption>{caption_esc}</figcaption>"
        else:
            caption_html = ""

        fig_html = f"""
        <figure class="gallery-item">
          <img src="/{img_path}" alt="{alt_text_esc}">
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
