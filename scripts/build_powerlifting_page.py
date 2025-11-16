import csv
from pathlib import Path
from textwrap import indent
import html
from datetime import datetime

# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # set to True later if you want captions under photos

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Catalogue path in Drive (adjust if needed)
CATALOGUE = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv")

# Template + output inside the repo
TEMPLATE = ROOT / "templates" / "powerlifting_template.html"
OUTPUT = ROOT / "powerlifting" / "index.html"


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


def parse_date_iso(s):
    """Try to parse ISO-ish datetime; return datetime or None."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def make_gallery_section_for_year(year, items):
    """
    year: string, e.g. "2023"
    items: list of dicts (rows) for that year
    """
    figures = []

    # Sort items by date descending if possible
    def sort_key(row):
        dt = parse_date_iso(row.get("post_datetime") or "")
        # sort newest first; None goes last
        return dt or datetime.min

    items_sorted = sorted(items, key=sort_key, reverse=True)

    for item in items_sorted:
        img_path = get_image_path(item)
        if not img_path:
            continue

        caption = (item.get("caption") or "").strip()
        alt_text = caption or "Powerlifting photo"

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

    section_title = year if year else "Unsorted"

    section_html = f"""
    <section class="gallery">
      <h2>{html.escape(section_title)}</h2>
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
