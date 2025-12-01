import subprocess
from pathlib import Path

from scripts.build_common import ROOT

# --------------------------------------
# CONFIG
# --------------------------------------

# Folder where your videos live
VIDEO_ROOT = ROOT / "assets" / "images" / "origami"

# Video extensions to process
VIDEO_EXTS = {".mp4", ".mov", ".webm"}

# Thumbnail extension
THUMB_EXT = ".jpg"

# Timestamp to grab the frame from (hh:mm:ss or similar)
THUMB_TIMESTAMP = "00:00:01"


def make_thumbnail_for_video(video_path: Path) -> None:
    """
    Given a video file, create a JPG thumbnail next to it
    with the same base name (if it doesn't already exist).
    """
    thumb_path = video_path.with_suffix(THUMB_EXT)

    if thumb_path.exists():
        print(f"[skip] Thumbnail already exists: {thumb_path}")
        return

    thumb_path.parent.mkdir(parents=True, exist_ok=True)

    # ffmpeg command:
    #   -ss <time>  seek to timestamp
    #   -i <input>  input file
    #   -vframes 1  output a single frame
    cmd = [
        "ffmpeg",
        "-y",  # overwrite if needed (though we skip if exists)
        "-ss", THUMB_TIMESTAMP,
        "-i", str(video_path),
        "-vframes", "1",
        str(thumb_path),
    ]

    print(f"[run] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[ok]  Created thumbnail: {thumb_path}")
    except subprocess.CalledProcessError as e:
        print(f"[err] Failed to create thumbnail for {video_path}")
        print("      ffmpeg stderr:")
        try:
            print(e.stderr.decode("utf-8", errors="ignore"))
        except Exception:
            pass


def build_powerlifting_thumbnails():
    if not VIDEO_ROOT.exists():
        print(f"Video root does not exist: {VIDEO_ROOT}")
        return

    print(f"Scanning for videos under: {VIDEO_ROOT}")

    count = 0
    for path in VIDEO_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() in VIDEO_EXTS:
            make_thumbnail_for_video(path)
            count += 1

    print(f"Done. Processed {count} video file(s).")


if __name__ == "__main__":
    build_powerlifting_thumbnails()
