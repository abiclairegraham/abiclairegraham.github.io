import csv
from pathlib import Path
from textwrap import indent
import html

# --------------------------------------
# CONFIG
# --------------------------------------
CAPTIONS_INCLUDE = False   # <<< change to True if you want captions later

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
    if "filename_relative" in row and row["filename_relative"]:_]()_
