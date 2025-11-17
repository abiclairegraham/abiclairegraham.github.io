# scripts/catalogue_instagram.py

from pathlib import Path
import csv
import json
from datetime import datetime

# You can tweak these defaults or override from Colab
INSTAGRAM_DIR = Path(
    "/content/drive/MyDrive/meta-2025-Nov-16-09-27-16/instagram-abi.graham.35-2025-11-16-QoA42s2j"
)
OUTPUT_CSV = Path(
    "/content/drive/MyDrive/Personal Projects/media_catalogue_instagram.csv"
)


def iter_instagram_posts(insta_dir: Path):
    """Yield (post_dict, json_path) from any posts_*.json-like files."""
    for json_path in insta_dir.rglob("*.json"):
        name = json_path.name.lower()
        if not ("post" in name or "media" in name):
            continue

        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            posts = data
        elif isinstance(data, dict):
            possible_lists = [v for v in data.values() if isinstance(v, list)]
            posts = possible_lists[0] if possible_lists else [data]
        else:
            continue

        for post in posts:
            yield post, json_path


def parse_instagram_post(post):
    """
    Extract timestamp, caption, and media list from a single post dict.
    Based directly on your Colab function.
    """
    # --- timestamp ---
    ts = (
        post.get("creation_timestamp")
        or post.get("taken_at")
        or post.get("media_creation_timestamp")
        or post.get("date")
    )

    first_media = None
    if "media" in post and isinstance(post["media"], list) and post["media"]:
        if isinstance(post["media"][0], dict):
            first_media = post["media"][0]

    if ts is None and first_media is not None:
        ts = (
            first_media.get("creation_timestamp")
            or first_media.get("taken_at")
            or first_media.get("media_creation_timestamp")
            or first_media.get("date")
        )

    dt_iso = ""
    if isinstance(ts, (int, float)):
        dt_iso = datetime.fromtimestamp(ts).isoformat()
    elif isinstance(ts, str):
        try:
            dt_iso = datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat()
        except Exception:
            dt_iso = ts

    # --- caption ---
    caption = (
        post.get("caption")
        or post.get("title")
        or post.get("description")
        or ""
    )

    if not caption and first_media is not None:
        caption = (
            first_media.get("caption")
            or first_media.get("title")
            or first_media.get("description")
            or ""
        )

    if isinstance(caption, dict):
        caption = caption.get("text") or ""

    # --- media URIs ---
    media_uris = []
    if "media" in post and isinstance(post["media"], list):
        for m in post["media"]:
            if not isinstance(m, dict):
                continue
            uri = m.get("uri") or m.get("path") or m.get("media_url")
            if uri:
                media_uris.append(uri)
    elif "media" in post and isinstance(post["media"], dict):
        uri = post["media"].get("uri") or post["media"].get("path")
        if uri:
            media_uris.append(uri)
    elif "uri" in post:
        media_uris.append(post["uri"])

    return dt_iso, caption, media_uris


def build_instagram_catalogue(
    insta_dir: Path = INSTAGRAM_DIR,
    output_csv: Path = OUTPUT_CSV,
):
    fieldnames = ["source", "filename_raw", "post_datetime", "caption", "json_source"]
    count_rows = 0

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for post, json_path in iter_instagram_posts(insta_dir):
            dt_iso, caption, media_uris = parse_instagram_post(post)
            if not media_uris:
                continue
            for uri in media_uris:
                row = {
                    "source": "instagram",
                    "filename_raw": uri,
                    "post_datetime": dt_iso,
                    "caption": caption,
                    "json_source": str(json_path.relative_to(insta_dir)),
                }
                writer.writerow(row)
                count_rows += 1

    print(f"Wrote {count_rows} rows to {output_csv}")


if __name__ == "__main__":
    build_instagram_catalogue()
