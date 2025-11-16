import csv
from pathlib import Path
from textwrap import indent
import html

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Catalogue path in Drive (adjust if needed)
CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv")

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

def make_gallery_section(title, items):
    figures = []

    for item in items:
        img_path = get_image_path(item)
        if not img_path:
            continue

        caption = (item.get("caption") or "").strip()
        alt_text = caption or "Origami model"

        alt_text_esc = html.escape(alt_text, quote=True)
        caption_esc = html.escape(caption)

        fig_html = f"""
        <figure class="gallery-item">
          <img src="/{img_path}" alt="{alt_text_esc}">
          <figcaption>{caption_esc}</figcaption>
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
    origami_rows = [r for r in rows if (r.get("section") or "").lower() == "origami"]

    sections_html = []
    for key, title in ORIGAMI_SUBSECTIONS:
        items = [r for r in origami_rows if (r.get("subsection") or "").lower() == key]
        section_html = make_gallery_section(title, items)
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
