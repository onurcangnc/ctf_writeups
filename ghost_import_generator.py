#!/usr/bin/env python3
"""
Ghost Import Generator
─────────────────────
Reads HackTheBox writeups, uploads images to Ghost via API,
generates a Ghost-compatible import JSON.

Usage:
  1. Run this script locally in your ctf_writeups repo root
  2. It uploads images to Ghost (API works for images)
  3. Generates ghost_import.json
  4. Go to Ghost Admin → Settings → Labs → Import → upload ghost_import.json
  5. Done — posts + images live in Ghost, independent of GitHub

Requirements:
  pip install PyJWT requests markdown
"""

import os
import re
import sys
import json
import time
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime, timezone

try:
    import jwt
    import requests
    import markdown
except ImportError:
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install PyJWT requests markdown --quiet")
    import jwt
    import requests
    import markdown

# ─── Configuration ───────────────────────────────────────────────────────────

GHOST_URL = os.environ.get("GHOST_URL", "https://blog.onurcangenc.com.tr")
GHOST_ADMIN_KEY = os.environ.get(
    "GHOST_ADMIN_API_KEY",
    "REDACTED_ADMIN_KEY",
)
GHOST_CONTENT_KEY = os.environ.get(
    "GHOST_CONTENT_API_KEY",
    "REDACTED_CONTENT_KEY",
)

BASE_DIR = "HackTheBox"
EXCLUDE_FILES = ["README.md", "index.md", "_index.md", "HTB_Easy_Machines_Roadmap.md"]
EXCLUDE_DIRS = [".obsidian", ".git", "templates", "attachments", "_templates", ".github", "scripts"]
IMAGE_CACHE = ".ghost_image_cache.json"


# ─── Ghost API Auth (JWT — works for image uploads) ─────────────────────────

def create_token(admin_key: str) -> str:
    key_id, secret = admin_key.split(":")
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 5 * 60, "aud": "/admin/"},
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"kid": key_id},
    )


def api_session() -> requests.Session:
    token = create_token(GHOST_ADMIN_KEY)
    s = requests.Session()
    s.headers["Authorization"] = f"Ghost {token}"
    return s


# ─── Image Cache ─────────────────────────────────────────────────────────────

def load_image_cache() -> dict:
    if os.path.exists(IMAGE_CACHE):
        with open(IMAGE_CACHE) as f:
            return json.load(f)
    return {}


def save_image_cache(cache: dict):
    with open(IMAGE_CACHE, "w") as f:
        json.dump(cache, f, indent=2)


def file_hash(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ─── Image Upload ────────────────────────────────────────────────────────────

def upload_image(session: requests.Session, image_path: Path, cache: dict) -> str:
    path_str = str(image_path)
    h = file_hash(path_str)

    if path_str in cache and cache[path_str]["hash"] == h:
        print(f"    ⊘ Cached: {image_path.name}")
        return cache[path_str]["url"]

    mime = mimetypes.guess_type(path_str)[0] or "image/png"
    with open(image_path, "rb") as f:
        r = session.post(
            f"{GHOST_URL}/ghost/api/admin/images/upload/",
            files={"file": (image_path.name, f, mime)},
            data={"purpose": "image", "ref": path_str},
        )

    if r.status_code == 201:
        url = r.json()["images"][0]["url"]
        cache[path_str] = {"hash": h, "url": url}
        print(f"    ✓ Uploaded: {image_path.name} → {url}")
        return url

    print(f"    ✗ Failed: {image_path.name} ({r.status_code})")
    return None


# ─── Markdown Processing ─────────────────────────────────────────────────────

def extract_title(content: str, filename: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filename.replace(".md", "").replace("-", " ").replace("_", " ").title()


def extract_description(content: str) -> str:
    content = re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)
    content = re.sub(r"^#\s+.+$", "", content, re.MULTILINE)
    paragraphs = re.findall(r"^[A-Za-z].+", content, re.MULTILINE)
    if paragraphs:
        return paragraphs[0][:300]
    return ""


def slugify(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def process_images(content: str, md_path: Path, session: requests.Session, cache: dict) -> str:
    """Replace image references with Ghost URLs."""
    writeup_dir = md_path.parent

    def replace_md_image(match):
        alt = match.group(1)
        ref = match.group(2)
        if ref.startswith(("http://", "https://")):
            return match.group(0)
        img = (writeup_dir / ref).resolve()
        if not img.exists():
            img = (writeup_dir / "images" / Path(ref).name).resolve()
        if img.exists():
            url = upload_image(session, img, cache)
            if url:
                return f"![{alt}]({url})"
        print(f"    ⚠ Not found: {ref}")
        return match.group(0)

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md_image, content)

    # Obsidian ![[image.png]]
    def replace_obsidian(match):
        name = match.group(1).split("/")[-1]
        img = writeup_dir / "images" / name
        if not img.exists():
            for p in writeup_dir.rglob(name):
                img = p
                break
        if img.exists():
            url = upload_image(session, img, cache)
            if url:
                return f"![{name}]({url})"
        return match.group(0)

    content = re.sub(r"!\[\[([^\]]+)\]\]", replace_obsidian, content)
    return content


def md_to_html(content: str) -> str:
    # Remove H1
    content = re.sub(r"^#\s+.+$", "", content, count=1, flags=re.MULTILINE)
    return markdown.markdown(
        content,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
        ],
    )


# ─── Ghost Import JSON Builder ───────────────────────────────────────────────

def build_ghost_import(posts: list) -> dict:
    """Build Ghost-compatible import JSON."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    ghost_posts = []
    ghost_tags = []
    posts_tags = []
    seen_tags = {}
    tag_counter = 1

    for i, p in enumerate(posts):
        post_id = str(670000000000 + i)

        ghost_post = {
            "id": post_id,
            "title": p["title"],
            "slug": p["slug"],
            "html": p["html"],
            "custom_excerpt": p["excerpt"][:300] if p["excerpt"] else None,
            "feature_image": p.get("feature_image"),
            "status": "published",
            "created_at": now,
            "updated_at": now,
            "published_at": now,
        }
        ghost_posts.append(ghost_post)

        # Tags
        for tag_name in p["tags"]:
            if tag_name not in seen_tags:
                tag_id = str(680000000000 + tag_counter)
                tag_counter += 1
                seen_tags[tag_name] = tag_id
                ghost_tags.append({
                    "id": tag_id,
                    "name": tag_name,
                    "slug": slugify(tag_name),
                })

            posts_tags.append({
                "post_id": post_id,
                "tag_id": seen_tags[tag_name],
            })

    return {
        "db": [{
            "meta": {
                "exported_on": int(time.time() * 1000),
                "version": "5.82.0",
            },
            "data": {
                "posts": ghost_posts,
                "tags": ghost_tags,
                "posts_tags": posts_tags,
            },
        }],
    }


# ─── Duplicate Detection ─────────────────────────────────────────────────────

def normalize_title(title: str) -> str:
    """Normalize title for fuzzy comparison."""
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def fetch_existing_titles(session: requests.Session) -> set:
    """Fetch all existing post titles from Ghost via Content API (read-only, no 403)."""
    titles = set()
    page = 1

    while True:
        r = requests.get(
            f"{GHOST_URL}/ghost/api/content/posts/",
            params={"key": GHOST_CONTENT_KEY, "fields": "title", "limit": 100, "page": page},
        )
        if r.status_code != 200:
            print(f"  ⚠ Could not fetch existing posts: {r.status_code}")
            return titles

        data = r.json()
        posts = data.get("posts", [])
        if not posts:
            break

        for p in posts:
            titles.add(normalize_title(p["title"]))

        meta = data.get("meta", {}).get("pagination", {})
        if page >= meta.get("pages", 1):
            break
        page += 1

    print(f"  Existing posts on Ghost: {len(titles)}")
    return titles


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("👻 Ghost Import Generator")
    print(f"  Ghost URL: {GHOST_URL}")
    print(f"  Scanning: {BASE_DIR}/\n")

    session = api_session()

    # Test connection
    r = session.get(f"{GHOST_URL}/ghost/api/admin/site/")
    if r.status_code != 200:
        print(f"❌ Cannot connect to Ghost: {r.status_code}")
        sys.exit(1)
    print(f"  Connected: {r.json()['site']['title']}\n")

    # Fetch existing posts for duplicate detection
    print("  Loading existing posts...")
    existing_titles = fetch_existing_titles(session)

    image_cache = load_image_cache()
    posts = []
    skipped = 0

    if not os.path.exists(BASE_DIR):
        print(f"❌ Directory '{BASE_DIR}' not found. Run this from your ctf_writeups repo root.")
        sys.exit(1)

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if not file.endswith(".md") or file in EXCLUDE_FILES:
                continue

            md_path = Path(root) / file
            parts = md_path.parts

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            title = extract_title(content, md_path.stem)

            # Extract machine name from folder: HackTheBox/Valentine/... → "valentine"
            machine_name = normalize_title(parts[1]) if len(parts) >= 2 else normalize_title(title)

            # Check if already on Ghost — match on machine name in any Ghost title
            match = None
            for ghost_title in existing_titles:
                if machine_name and machine_name in ghost_title:
                    match = ghost_title
                    break

            if match:
                print(f"⊘ Skipping (already on Ghost): {title}  [{machine_name} ≈ '{match}']")
                skipped += 1
                continue

            print(f"\n📄 {md_path}")
            excerpt = extract_description(content)
            slug = slugify(title)
            tags = ["HackTheBox", "writeup"]
            if len(parts) >= 2:
                tags.insert(1, parts[1])

            print(f"  Title: {title}")
            print(f"  Uploading images...")

            processed = process_images(content, md_path, session, image_cache)
            save_image_cache(image_cache)

            html = md_to_html(processed)

            # Feature image = first image in images/ dir
            feature_image = None
            images_dir = md_path.parent / "images"
            if images_dir.exists():
                for ext in ["*.png", "*.jpg", "*.jpeg"]:
                    imgs = sorted(images_dir.glob(ext))
                    if imgs:
                        feature_image = upload_image(session, imgs[0], image_cache)
                        save_image_cache(image_cache)
                        break

            posts.append({
                "title": title,
                "slug": slug,
                "html": html,
                "excerpt": excerpt,
                "tags": tags,
                "feature_image": feature_image,
            })
            print()

    if not posts:
        print(f"\n⚠ No new writeups to import. ({skipped} already on Ghost)")
        sys.exit(0)

    # Generate import JSON
    import_data = build_ghost_import(posts)
    output_file = "ghost_import.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(import_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"✅ Generated: {output_file}")
    print(f"   New posts: {len(posts)}")
    print(f"   Skipped:   {skipped} (already on Ghost)")
    print(f"\n📋 Next steps:")
    print(f"   1. Ghost Admin → Settings → Labs → Import")
    print(f"   2. Upload {output_file}")
    print(f"   3. Done! All posts with Ghost-hosted images.")


if __name__ == "__main__":
    main()
