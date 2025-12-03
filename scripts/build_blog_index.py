import re
import html
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Repo root (this script lives in scripts/)
ROOT = Path(__file__).resolve().parent.parent

# Where blog posts live now
BLOG_ROOT = ROOT / "blog"
POSTS_DIR = BLOG_ROOT / "posts"

TEMPLATE = ROOT / "templates" / "blog_index_template.html"
OUTPUT = BLOG_ROOT / "index.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_meta(content: str, name: str) -> str:
    """
    Find <meta name="name" content="..."> and return the content.
    Very lightweight regex-based extractor.
    """
    pattern = rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']+)["\']'
    m = re.search(pattern, content, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_first_tag_text(content: str, tag: str) -> str:
    """
    Extract raw inner HTML for the first <tag>...</tag>, then strip any nested tags.
    """
    pattern = rf"<{tag}[^>]*>(.*?)</{tag}>"
    m = re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    inner = m.group(1)
    # Strip nested tags
    inner = re.sub(r"<[^>]+>", "", inner)
    return inner.strip()


def extract_first_img_src(content: str) -> str:
    """
    Find the first <img ... src="..."> and return the src value.
    """
    m = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', content, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_date(date_str: str):
    """
    Parse YYYY-MM-DD (or similar) into a datetime for sorting.
    Very forgiving: if parsing fails, return None.
    """
    if not date_str:
        return None
    # Try a few common formats
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            # slice to match fmt length when there are extras
            return datetime.strptime(date_str[:len(fmt)], fmt)
        except Exception:
            continue
    return None


def summarise(text: str, max_len: int = 200) -> str:
    """
    Simple summary: truncate at max_len and add '…' if needed.
    """
    text = " ".join(text.split())  # collapse whitespace
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def extract_post_metadata(path: Path):
    """
    Extract title, date, year, summary, thumbnail, url from a blog post HTML file.
    """
    content = read_text(path)

    title = extract_first_tag_text(content, "h1")
    date_str = extract_meta(content, "post-date")
    summary_meta = extract_meta(content, "post-summary")
    thumb_meta = extract_meta(content, "post-thumbnail")

    # Fallbacks
    if not summary_meta:
        first_p = extract_first_tag_text(content, "p")
        summary_meta = summarise(first_p) if first_p else ""

    if not thumb_meta:
        thumb_meta = extract_first_img_src(content)

    dt = parse_date(date_str)
    year = str(dt.year) if dt else "Articles"

    # URL is /blog/posts/<filename>
    url = "/blog/posts/" + path.name

    return {
        "title": title or path.stem,
        "date_str": date_str,
        "year": year,
        "summary": summary_meta,
        "thumbnail": thumb_meta,
        "url": url,
        "sort_key": dt or datetime.min,
    }


def build_post_card(post):
    """
    Build HTML for a single blog card.
    """
    title = html.escape(post["title"])
    summary = html.escape(post["summary"])
    date_str = html.escape(post["date_str"] or "")
    url = html.escape(post["url"])
    thumb = post["thumbnail"]

    if thumb:
        thumb_html = f"""
        <div class="blog-card-thumb">
          <img src="{html.escape(thumb)}" alt="">
        </div>
        """.rstrip()
    else:
        thumb_html = ""

    card_html = f"""
    <a class="blog-card" href="{url}">
      {thumb_html}
      <div class="blog-card-body">
        <h3 class="blog-card-title">☞ {title}</h3>
        <p class="blog-card-meta">{date_str}</p>
        <p class="blog-card-summary">{summary}</p>
      </div>
    </a>  
    """.rstrip()

    return card_html


def build_blog_index():
    if not POSTS_DIR.exists():
        print("Posts directory does not exist:", POSTS_DIR)
        return

    # Collect posts from blog/posts/*.html
    posts = []
    for path in POSTS_DIR.glob("*.html"):
        meta = extract_post_metadata(path)
        posts.append(meta)

    if not posts:
        post_list_html = "<p>No blog posts yet.</p>"
    else:
        # Sort newest first
        posts.sort(key=lambda p: p["sort_key"], reverse=True)

        # Group by year
        by_year = defaultdict(list)
        for p in posts:
            by_year[p["year"]].append(p)

        years_sorted = sorted(
            [y for y in by_year.keys() if y != "Unknown"],
            reverse=True
        )
        if "Unknown" in by_year:
            years_sorted.append("Unknown")

        year_sections = []
        for year in years_sorted:
            cards = [build_post_card(p) for p in by_year[year]]
            cards_html = "\n\n".join(cards)
            section_html = f"""
      <section class="blog-year-section">
        <h2 class="blog-year-heading">{html.escape(year)}</h2>
        <div class="blog-card-list">
{cards_html}
        </div>
      </section>
            """.rstrip()
            year_sections.append(section_html)

        post_list_html = "\n\n".join(year_sections)

    template = TEMPLATE.read_text(encoding="utf-8")
    final_html = template.replace("{{POST_LIST}}", post_list_html)

    OUTPUT.write_text(final_html, encoding="utf-8")
    print(f"Wrote blog index → {OUTPUT}")


if __name__ == "__main__":
    build_blog_index()
