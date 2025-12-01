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

    # Meta block (date + subs
