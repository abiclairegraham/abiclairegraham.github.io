# scripts/catalogue_copy_images.py

from pathlib import Path
import csv
import re
import shutil

INSTAGRAM_DIR = Path("/content/drive/MyDrive/meta-2025-Nov-16-09-27-16/instagram-...")  # same as before
REPO_ROOT = Path("/content/drive/MyDrive/Personal Projects/abiclairegraham.github.io")

CATALOG_IN = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_labeled.csv")
CATALOG_WITH_POSTS = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_posts.csv")
CATALOG_OUT = Path("/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv")

def slugify(text, max_len=60):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "post"
  
def add_post_keys_and_slugs():
    # your existing IN_PATH → OUT_PATH code (with variable names adjusted)
    rows = []
    with CATALOG_IN.open("r", encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)
        if "post_key" not in fieldnames:
            fieldnames.append("post_key")
        if "post_slug" not in fieldnames:
            fieldnames.append("post_slug")
    
        for row in reader:
            source = row.get("source", "") or "instagram"
            dt = row.get("post_datetime", "") or ""
            js = row.get("json_source", "") or ""
            section = (row.get("section") or "general").lower()
            caption = (row.get("caption") or "").strip()
    
            post_key = f"{source}::{dt}::{js}"
            # base slug: section + date + bit of caption
            caption_snippet = caption.split("\n", 1)[0]  # first line
            base_slug = f"{section}-{dt[:10]}-{caption_snippet}"
            post_slug = slugify(base_slug)
    
            row["post_key"] = post_key
            row["post_slug"] = post_slug
            rows.append(row)
    
    with CATALOG_WITH_POSTS.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    
    print("Wrote", len(rows), "rows to", CATALOG_WITH_POSTS)
    return

def decide_dest_relpath(row):
    """
    Decide where in the repo we want this image to live, relative to repo root.
    Returns a Path (relative), or None to skip.
    """
    section = (row.get("section") or "").lower()
    subsection = (row.get("subsection") or "").lower()
    filename_raw = row.get("filename_raw") or ""
    filename_raw = filename_raw.lstrip("/")  # in case it starts with "/"

    src_name = Path(filename_raw).name  # keep original filename for now

    if not section:
        return None

    base = Path("assets/images")

    if section == "origami":
        # subsection: insects / animals / tessellations / curved / modular
        subdir = subsection if subsection else "general"
        dest_dir = base / "origami" / subdir

    elif section == "powerlifting":
        # subsection is year, e.g. "2023"
        year = subsection if subsection else "unknown-year"
        dest_dir = base / "powerlifting" / year

    elif section == "makeup":
        dest_dir = base / "makeup"

    elif section == "singing":
        dest_dir = base / "singing"

    elif section == "activism":
        dest_dir = base / "activism"

    elif section == "craft":
        dest_dir = base / "craft"

    elif section == "general":
        dest_dir = base / "general"

    else:
        # if you don't have a section/page yet, skip or send to a misc folder
        dest_dir = base / "misc"

    return dest_dir / src_name

def copy_images_and_write_catalogue():
    # -----------------------
    # CLEAN OUT OLD IMAGE FOLDERS
    # -----------------------
    
    IMG_ROOT = REPO_ROOT / "assets" / "images"
    
    print("Clearing existing images under:", IMG_ROOT)
    
    if IMG_ROOT.exists():
        for item in IMG_ROOT.iterdir():
            if item.is_dir():
                print("  Removing folder:", item)
                shutil.rmtree(item)
            else:
                print("  Removing file:", item)
                item.unlink()
    else:
        IMG_ROOT.mkdir(parents=True, exist_ok=True)
    
    print("Image folders wiped.\n")
    
    
    # -----------------------
    # Main copy + catalogue update
    # -----------------------
    
    rows = []
    with CATALOG_WITH_POSTS.open("r", encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)
    
        if "filename_relative" not in fieldnames:
            fieldnames.append("filename_relative")
    
        for row in reader:
            rows.append(row)
    
    copied = 0
    missing = 0
    
    for row in rows:
        filename_raw = (row.get("filename_raw") or "").lstrip("/")
        if not filename_raw:
            row["filename_relative"] = ""
            continue
    
        dest_rel = decide_dest_relpath(row)
        if dest_rel is None:
            row["filename_relative"] = ""
            continue
    
        # Source path in the archive
        src_path = INSTAGRAM_DIR / filename_raw
    
        # Destination path in the repo
        dest_path = REPO_ROOT / dest_rel
    
        if not src_path.exists():
            missing += 1
            print("Missing source file:", src_path)
            row["filename_relative"] = ""
            continue
    
        dest_path.parent.mkdir(parents=True, exist_ok=True)
    
        # Copy file (overwrite if exists)
        try:
            shutil.copy2(src_path, dest_path)
            row["filename_relative"] = str(dest_rel).replace("\\", "/")
            copied += 1
        except FileNotFoundError as e:
            print(f"Error copying {src_path} to {dest_path}: {e}")
            # Mark as failed or skip, depending on desired behavior
            row["filename_relative"] = "" # Or some error indicator
            missing += 1 # Count as missing for this operation, even if src exists
    
    print(f"Copied {copied} files into repo.")
    print(f"Missing {missing} source files.")
    
    with CATALOG_OUT.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    
    print("Wrote updated catalogue with filename_relative →", CATALOG_OUT)

def run_all():
    add_post_keys_and_slugs()
    copy_images_and_write_catalogue()

if __name__ == "__main__":
    run_all()
