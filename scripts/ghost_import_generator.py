#!/usr/bin/env python3
"""
Ghost Import Generator
─────────────────────
Reads HackTheBox writeups, uploads images to Ghost via API,
generates a Ghost-compatible import JSON.

If Ghost Admin API is unreachable (e.g. Cloudflare blocking CI),
falls back to GitHub raw URLs for images and still generates the artifact.

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
GHOST_ADMIN_KEY = os.environ.get("GHOST_ADMIN_API_KEY", "")
GHOST_CONTENT_KEY = os.environ.get("GHOST_CONTENT_API_KEY", "")

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/onurcangnc/ctf_writeups/main"

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
    s.headers["User-Agent"] = "CTFWriteups-GhostSync/1.0 (GitHub-Actions)"
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


# ─── Image Handling ─────────────────────────────────────────────────────────

def github_raw_url(image_path: Path) -> str:
    """Generate a GitHub raw URL for an image."""
    relative = image_path.as_posix()
    return f"{GITHUB_RAW_BASE}/{relative}"


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


def resolve_image_url(image_path: Path, session, cache: dict, use_ghost: bool) -> str:
    """Upload to Ghost if possible, otherwise use GitHub raw URL."""
    if use_ghost:
        url = upload_image(session, image_path, cache)
        if url:
            return url
    url = github_raw_url(image_path)
    print(f"    🔗 GitHub URL: {image_path.name}")
    return url


# ─── Markdown Processing ─────────────────────────────────────────────────────

def extract_title(content: str, filename: str) -> str:
    return filename.replace(".md", "").replace("-", " ").replace("_", " ")


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


def process_images(content: str, md_path: Path, session, cache: dict, use_ghost: bool) -> str:
    """Replace image references with Ghost or GitHub URLs."""
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
            # Get a relative path from repo root for GitHub URLs
            try:
                rel = img.relative_to(Path.cwd())
            except ValueError:
                rel = img
            url = resolve_image_url(rel, session, cache, use_ghost)
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
            try:
                rel = img.relative_to(Path.cwd())
            except ValueError:
                rel = img
            url = resolve_image_url(rel, session, cache, use_ghost)
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


def fetch_existing_titles() -> set:
    """Fetch all existing post titles from Ghost via Content API (no auth needed)."""
    if not GHOST_CONTENT_KEY:
        return set()

    titles = set()
    page = 1

    while True:
        try:
            r = requests.get(
                f"{GHOST_URL}/ghost/api/content/posts/",
                params={"key": GHOST_CONTENT_KEY, "fields": "title", "limit": 100, "page": page},
                timeout=10,
            )
        except requests.RequestException as e:
            print(f"  ⚠ Could not fetch existing posts: {e}")
            return titles

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

    if not GHOST_ADMIN_KEY or not GHOST_CONTENT_KEY:
        print("❌ GHOST_ADMIN_API_KEY and GHOST_CONTENT_API_KEY must be set as environment variables.")
        sys.exit(1)

    # Try Ghost Admin API — fall back to GitHub raw URLs if blocked
    use_ghost = False
    session = None
    try:
        session = api_session()
        r = session.get(f"{GHOST_URL}/ghost/api/admin/site/", timeout=10)
        if r.status_code == 200:
            use_ghost = True
            print(f"  ✓ Connected to Ghost: {r.json()['site']['title']}")
        else:
            print(f"  ⚠ Ghost Admin API returned {r.status_code} — using GitHub raw URLs for images")
    except requests.RequestException as e:
        print(f"  ⚠ Ghost Admin API unreachable ({e}) — using GitHub raw URLs for images")

    print()

    # Fetch existing posts for duplicate detection (Content API — usually not blocked)
    print("  Loading existing posts...")
    existing_titles = fetch_existing_titles()

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

            # Note: existence check moved to publish_to_ghost (POST vs PUT)
            # Mod 2: always queue, publish_to_ghost decides create vs update

            print(f"\n📄 {md_path}")
            excerpt = extract_description(content)
            slug = slugify(title)
            tags = ["HackTheBox", "writeup"]
            if len(parts) >= 2:
                tags.insert(1, parts[1])

            print(f"  Title: {title}")
            print(f"  Processing images...")

            processed = process_images(content, md_path, session, image_cache, use_ghost)
            if use_ghost:
                save_image_cache(image_cache)

            html = md_to_html(processed)

            # Feature image = first image in images/ dir
            feature_image = None
            images_dir = md_path.parent / "images"
            if images_dir.exists():
                for ext in ["*.png", "*.jpg", "*.jpeg"]:
                    imgs = sorted(images_dir.glob(ext))
                    if imgs:
                        try:
                            rel = imgs[0].relative_to(Path.cwd())
                        except ValueError:
                            rel = imgs[0]
                        feature_image = resolve_image_url(rel, session, image_cache, use_ghost)
                        if use_ghost:
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
        print(f"\n⚠ No writeups found.")
        sys.exit(0)

    # Generate import JSON (backup, manual fallback)
    import_data = build_ghost_import(posts)
    output_file = "ghost_import.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(import_data, f, indent=2, ensure_ascii=False)

    mode = "Ghost-hosted" if use_ghost else "GitHub raw"
    print(f"\n{'='*50}")
    print(f"✅ Generated: {output_file}")
    print(f"   Posts: {len(posts)}")
    print(f"   Images: {mode} URLs")

    # Mod 2: Auto-publish (create or update) via Ghost Admin API
    if use_ghost:
        print(f"\n📤 Syncing {len(posts)} posts to Ghost (create/update)...")
        created, updated, failed = publish_to_ghost(posts, session)
        print(f"\n{'='*50}")
        print(f"✅ Sync complete")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
        print(f"   Failed:  {failed}")
        if failed > 0:
            print(f"\n⚠ {failed} posts failed — check {output_file} for backup")
        else:
            print(f"\n✓ All posts live. ghost_import.json kept as backup.")
    else:
        print(f"\n⚠ Ghost connection unavailable — manual import required:")
        print(f"   1. Ghost Admin → Settings → Labs → Import")
        print(f"   2. Upload {output_file}")


def _extract_machine_name(title: str) -> str:
    """Extract the unique machine identifier from a writeup title.

    Examples:
      "HTB Topology"               -> "Topology"
      "HTB Bashed Writeup"         -> "Bashed"
      "HTB Devvortex: from Joomla" -> "Devvortex"
      "Topology"                   -> "Topology"
    """
    parts = re.split(r"[\s:—-]+", title.strip())
    parts = [p for p in parts if p]
    if not parts:
        return ""
    # Skip leading "HTB" prefix if present
    if parts[0].upper() == "HTB" and len(parts) > 1:
        return parts[1]
    return parts[0]


def find_existing_post(slug: str, title: str, session: requests.Session) -> dict | None:
    """Ghost'ta bu post var mı? 2 aşamalı match:
       1) Direkt slug match (htb-topology = htb-topology)
       2) Title fuzzy match — machine name title'da geçiyor mu (htb-bashed-writeup-from-...)
       Returns: post object (id, updated_at, title, slug) veya None
    """
    # 1) Direct slug match
    try:
        r = session.get(
            f"{GHOST_URL}/ghost/api/admin/posts/slug/{slug}/",
            params={"fields": "id,updated_at,title,slug"},
            timeout=15,
        )
        if r.status_code == 200:
            posts_list = r.json().get("posts", [])
            if posts_list:
                return posts_list[0]
    except Exception:
        pass

    # 2) Title fuzzy match — machine name in title
    machine = _extract_machine_name(title)
    if not machine or len(machine) < 3:
        return None
    try:
        # NQL: title contains 'Bashed' (case-insensitive in Ghost)
        r = session.get(
            f"{GHOST_URL}/ghost/api/admin/posts/",
            params={
                "filter": f"title:~'{machine}'",
                "fields": "id,updated_at,title,slug",
                "limit": 5,
            },
            timeout=15,
        )
        if r.status_code == 200:
            posts_list = r.json().get("posts", [])
            for p in posts_list:
                # Strict: machine adı title'da gerçekten var (büyük/küçük harf duyarsız)
                if machine.lower() in (p.get("title", "") or "").lower():
                    return p
    except Exception:
        pass

    return None


def publish_to_ghost(posts: list, session: requests.Session) -> tuple:
    """Her post'u Ghost'a POST (yeni) veya PUT (mevcut) et.

    Returns: (created, updated, failed)
    """
    created = 0
    updated = 0
    failed = 0

    for p in posts:
        slug = p["slug"]
        tag_objs = [{"name": t} for t in p.get("tags", [])]
        post_data = {
            "title": p["title"],
            "slug": slug,
            "html": p["html"],
            "custom_excerpt": (p.get("excerpt", "") or "")[:300],
            "tags": tag_objs,
            "status": "published",
        }
        if p.get("feature_image"):
            post_data["feature_image"] = p["feature_image"]

        existing = find_existing_post(slug, p["title"], session)

        try:
            if existing:
                # Existing post bulundu — slug match veya title fuzzy match
                # PUT için MEVCUT slug'u koru (Ghost'taki canonical URL kalsın)
                post_data["slug"] = existing.get("slug", slug)
                post_data["updated_at"] = existing["updated_at"]

                match_type = "slug" if existing.get("slug") == slug else f"title→{existing.get('slug')}"
                r = session.put(
                    f"{GHOST_URL}/ghost/api/admin/posts/{existing['id']}/?source=html",
                    json={"posts": [post_data]},
                    timeout=60,
                )
                if r.status_code == 200:
                    updated_post = r.json()["posts"][0]
                    print(f"  ↻ Updated [{match_type}]: {p['title']} → {updated_post.get('url', '')}")
                    updated += 1
                else:
                    print(f"  ✗ Update failed ({r.status_code}): {p['title']}")
                    print(f"    {r.text[:200]}")
                    failed += 1
            else:
                # POST (create)
                r = session.post(
                    f"{GHOST_URL}/ghost/api/admin/posts/?source=html",
                    json={"posts": [post_data]},
                    timeout=60,
                )
                if r.status_code in (200, 201):
                    new_post = r.json()["posts"][0]
                    print(f"  ✓ Created: {p['title']} → {new_post.get('url', '')}")
                    created += 1
                else:
                    print(f"  ✗ Create failed ({r.status_code}): {p['title']}")
                    print(f"    {r.text[:200]}")
                    failed += 1
        except Exception as e:
            print(f"  ✗ Exception: {p['title']} → {e}")
            failed += 1

        time.sleep(1)  # Ghost rate limit: 100 req/5min

    return created, updated, failed


if __name__ == "__main__":
    main()
