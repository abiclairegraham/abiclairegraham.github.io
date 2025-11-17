"""
build_common.py
This is where I am keeping shared commonly used functions and also the main configurations like paths etc...
Hopefully this will simplify things, see what's going on and make it easier to make changes without breaking things.
"""

from pathlib import Path
from datetime import datetime
import csv
import re

# ---------------------------------
# Paths / config
# ---------------------------------

# Root of the repo (scripts/ is one level down)
ROOT = Path(__file__).resolve().parent.parent

# Single source of truth for the main catalogue path
# (you can change this in ONE place later)
CATALOGUE_PATH = Path(
    "/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv"
)


# ---------------------------------
# Generic helpers
# ---------------------------------

def load_catalogue(path: Path | None = None) -> list[dict]:
    """
    Load the main media catalogue CSV as a list of dict rows.
    """
    if path is None:
        path = CATALOGUE_PATH

    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_image_path(row: dict) -> str:
    """
    Decide which image path to use for an item:
    - prefer filename_relative (repo-relative path)
    - else fall back to filename_raw (archive path)
    Returns a string without a leading slash.
    """
    rel = (row.get("filename_relative") or "").lstrip("/")
    if rel:
        return rel

    raw = (row.get("filename_raw") or "").lstrip("/")
    if raw:
        return raw

    return ""


def parse_iso_date(s: str | None) -> datetime | None:
    """
    Try to parse a date/time string into a datetime, or return None.
    Mainly used for sorting posts.
    """
    if not s:
        return None

    # If you know everything is ISO, datetime.fromisoformat would be enough.
    # We'll be a bit forgiving, like in your blog script.
    candidates = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(s[: len(fmt)], fmt)
        except Exception:
            continue
    return None


def slugify(text: str, max_len: int = 80) -> str:
    """
    Normalise text into a URL-safe slug.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "post"


def make_post_key(row: dict) -> str:
    """
    Build a consistent 'post key' from row metadata.
    Used to group multiple images that came from the same post.
    """
    source = row.get("source", "") or "instagram"
    dt = row.get("post_datetime", "") or ""
    js = row.get("json_source", "") or ""
    return f"{source}::{dt}::{js}"


def make_post_slug(row: dict) -> str:
    """
    Get a URL slug for this post.

    Preferred:
      - use the post_slug column from the catalogue (source of truth)

    Fallback:
      - derive from section + date + post_key in a deterministic way
    """
    raw_slug = (row.get("post_slug") or "").strip()
    if raw_slug:
        return slugify(raw_slug)

    # Fallback path if for some reason post_slug is missing
    section = (row.get("section") or "post").lower()
    dt = row.get("post_datetime", "") or ""
    date_part = dt[:10] if len(dt) >= 10 else "unknown-date"
    post_key = make_post_key(row)

    base = f"{section}-{date_part}-{post_key}"
    return slugify(base)


def group_rows_by_post(rows: list[dict]) -> dict[str, list[dict]]:
    """
    Group a list of catalogue rows into {post_key: [rows...]}.
    """
    groups: dict[str, list[dict]] = {}
    for r in rows:
        key = make_post_key(r)
        groups.setdefault(key, []).append(r)
    return groups
