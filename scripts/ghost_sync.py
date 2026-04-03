#!/usr/bin/env python3
"""
Ghost Auto-Publisher
Syncs CTF writeups from GitHub repo to Ghost CMS.
- Uploads images to Ghost storage (independent of GitHub)
- Replaces local image paths with Ghost URLs
- Creates or updates posts via Ghost Admin API
- Tags posts by category (HackTheBox, TryHackMe, etc.)
"""

import os
import re
import sys
import json
import time
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime

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

BASE_DIRS = [
    "HackTheBox",
]

EXCLUDE_FILES = ["README.md", "TryHackMe.md", "index.md", "_index.md", "HTB_Easy_Machines_Roadmap.md"]
EXCLUDE_DIRS = [".obsidian", ".git", "templates", "attachments", "_templates", ".github", "scripts"]

# Track uploaded images to avoid re-uploading
CACHE_FILE = ".ghost_sync_cache.json"


# ─── Ghost Admin API Auth ────────────────────────────────────────────────────

def create_ghost_token(admin_key: str) -> str:
    """Create a Ghost Admin API JWT token."""
    key_id, secret = admin_key.split(":")
    iat = int(time.time())
    payload = {
        "iat": iat,
        "exp": iat + 5 * 60,
        "aud": "/admin/",
    }
    token = jwt.encode(
        payload,
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": key_id},
    )
    return token


def ghost_session(admin_key: str) -> requests.Session:
    """Create an authenticated requests session for Ghost Admin API."""
    token = create_ghost_token(admin_key)
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Ghost {token}",
    })
    return s


def get_owner_id(session: requests.Session) -> str | None:
    """Fetch the Owner user ID from Ghost — needed for integration post creation."""
    url = f"{GHOST_URL}/ghost/api/admin/users/?filter=role:Owner"
    r = session.get(url)
    if r.status_code == 200:
        users = r.json().get("users", [])
        if users:
            print(f"  Owner: {users[0]['name']} (id: {users[0]['id']})")
            return users[0]["id"]
    # Fallback: try to get any user
    url = f"{GHOST_URL}/ghost/api/admin/users/"
    r = session.get(url)
    if r.status_code == 200:
        users = r.json().get("users", [])
        if users:
            print(f"  Author: {users[0]['name']} (id: {users[0]['id']})")
            return users[0]["id"]
    print("  ⚠ Could not fetch owner ID")
    return None


# ─── Cache Management ────────────────────────────────────────────────────────

def load_cache() -> dict:
    """Load sync cache from file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"images": {}, "posts": {}}


def save_cache(cache: dict):
    """Save sync cache to file."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def file_hash(filepath: str) -> str:
    """Get MD5 hash of a file for change detection."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ─── Image Upload ────────────────────────────────────────────────────────────

def upload_image_to_ghost(session: requests.Session, image_path: Path, cache: dict) -> str:
    """Upload an image to Ghost and return the Ghost URL."""
    path_str = str(image_path)
    current_hash = file_hash(path_str)

    # Check cache - skip if already uploaded and unchanged
    if path_str in cache["images"] and cache["images"][path_str]["hash"] == current_hash:
        print(f"    ⊘ Cached: {image_path.name}")
        return cache["images"][path_str]["url"]

    url = f"{GHOST_URL}/ghost/api/admin/images/upload/"

    mime_type = mimetypes.guess_type(path_str)[0] or "image/png"
    
    with open(image_path, "rb") as f:
        files = {
            "file": (image_path.name, f, mime_type),
        }
        data = {
            "purpose": "image",
            "ref": path_str,
        }
        r = session.post(url, files=files, data=data)

    if r.status_code == 201:
        ghost_url = r.json()["images"][0]["url"]
        cache["images"][path_str] = {"hash": current_hash, "url": ghost_url}
        print(f"    ✓ Uploaded: {image_path.name} → {ghost_url}")
        return ghost_url
    else:
        print(f"    ✗ Failed to upload {image_path.name}: {r.status_code} {r.text[:200]}")
        return None


# ─── Markdown Processing ─────────────────────────────────────────────────────

def extract_title(content: str, filename: str) -> str:
    """Extract title from markdown H1 or filename."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filename.replace(".md", "").replace("-", " ").replace("_", " ").title()


def extract_description(content: str) -> str:
    """Extract first meaningful paragraph as excerpt."""
    # Remove frontmatter
    content = re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)
    # Remove H1
    content = re.sub(r"^#\s+.+$", "", content, re.MULTILINE)
    # Find first paragraph
    paragraphs = re.findall(r"^[A-Za-z].+", content, re.MULTILINE)
    if paragraphs:
        desc = paragraphs[0][:300]
        if len(paragraphs[0]) > 300:
            desc += "..."
        return desc
    return ""


def process_images_in_markdown(
    content: str,
    md_path: Path,
    session: requests.Session,
    cache: dict,
) -> str:
    """Find all image references in markdown, upload to Ghost, replace paths."""

    writeup_dir = md_path.parent

    def replace_image(match):
        alt_text = match.group(1)
        image_ref = match.group(2)

        # Handle relative paths (./images/1.png, images/1.png, ../images/1.png)
        if image_ref.startswith(("http://", "https://")):
            # Already an absolute URL - skip
            return match.group(0)

        # Resolve relative path from writeup directory
        image_path = (writeup_dir / image_ref).resolve()

        if not image_path.exists():
            # Try common patterns
            for alt_path in [
                writeup_dir / "images" / Path(image_ref).name,
                writeup_dir / image_ref.lstrip("./"),
            ]:
                if alt_path.exists():
                    image_path = alt_path.resolve()
                    break

        if image_path.exists():
            ghost_url = upload_image_to_ghost(session, image_path, cache)
            if ghost_url:
                return f"![{alt_text}]({ghost_url})"

        print(f"    ⚠ Image not found: {image_ref}")
        return match.group(0)

    # Standard markdown images: ![alt](path)
    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, content)

    # Obsidian-style images: ![[image.png]]
    def replace_obsidian_image(match):
        image_name = match.group(1).split("/")[-1]  # Get basename
        image_path = writeup_dir / "images" / image_name

        if not image_path.exists():
            # Search in writeup dir
            for p in writeup_dir.rglob(image_name):
                image_path = p
                break

        if image_path.exists():
            ghost_url = upload_image_to_ghost(session, image_path, cache)
            if ghost_url:
                return f"![{image_name}]({ghost_url})"

        print(f"    ⚠ Obsidian image not found: {image_name}")
        return match.group(0)

    content = re.sub(r"!\[\[([^\]]+)\]\]", replace_obsidian_image, content)

    return content


def markdown_to_ghost_html(content: str) -> str:
    """Convert markdown to HTML suitable for Ghost."""
    # Remove H1 (Ghost uses title field separately)
    content = re.sub(r"^#\s+.+$", "", content, count=1, flags=re.MULTILINE)

    # Convert markdown to HTML
    extensions = [
        "markdown.extensions.fenced_code",
        "markdown.extensions.tables",
        "markdown.extensions.codehilite",
        "markdown.extensions.toc",
        "markdown.extensions.nl2br",
    ]
    html = markdown.markdown(content, extensions=extensions)

    return html


# ─── Ghost Post Management ───────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Create a URL-safe slug from text."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def get_existing_post(session: requests.Session, slug: str) -> dict | None:
    """Check if a post with this slug already exists."""
    url = f"{GHOST_URL}/ghost/api/admin/posts/slug/{slug}/"
    r = session.get(url)
    if r.status_code == 200:
        posts = r.json().get("posts", [])
        if posts:
            return posts[0]
    return None


def post_exists_on_ghost(session: requests.Session, slug: str) -> bool:
    """Check if a post with this slug already exists on Ghost."""
    existing = get_existing_post(session, slug)
    return existing is not None


def create_post(
    session: requests.Session,
    title: str,
    slug: str,
    html: str,
    excerpt: str,
    tags: list[dict],
    feature_image: str = None,
    author_id: str = None,
) -> bool:
    """Create a new Ghost post. Skips if already exists."""

    url = f"{GHOST_URL}/ghost/api/admin/posts/?source=html"

    post_data = {
        "title": title,
        "slug": slug,
        "html": html,
        "custom_excerpt": excerpt[:300] if excerpt else None,
        "tags": tags,
        "status": "published",
    }

    if feature_image:
        post_data["feature_image"] = feature_image

    if author_id:
        post_data["authors"] = [{"id": author_id}]

    r = session.post(url, json={"posts": [post_data]})
    if r.status_code == 201:
        print(f"  ✓ Created: {title}")
        return True
    else:
        print(f"  ✗ Create failed: {r.status_code} {r.text[:300]}")
        return False


# ─── Main Sync Logic ─────────────────────────────────────────────────────────

def get_tags_for_path(md_path: Path) -> list[dict]:
    """Generate Ghost tags based on file path."""
    parts = md_path.parts
    tags = []

    # Category tag (e.g., HackTheBox, TryHackMe)
    if len(parts) >= 1 and parts[0] in BASE_DIRS:
        tags.append({"name": parts[0]})

    # Subcategory/machine name tag
    if len(parts) >= 2:
        tags.append({"name": parts[1]})

    # Always add writeup tag
    tags.append({"name": "writeup"})

    return tags


def find_feature_image(md_path: Path) -> Path | None:
    """Find the first image in the writeup's images directory for feature image."""
    images_dir = md_path.parent / "images"
    if images_dir.exists():
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp"]:
            images = sorted(images_dir.glob(ext))
            if images:
                return images[0]
    return None


def discover_writeups() -> list[Path]:
    """Find all markdown writeup files."""
    writeups = []

    for base_dir in BASE_DIRS:
        if not os.path.exists(base_dir):
            continue

        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file.endswith(".md") and file not in EXCLUDE_FILES:
                    writeups.append(Path(root) / file)

    return writeups


def should_sync(md_path: Path, cache: dict) -> bool:
    """Check if a writeup needs syncing (new or changed)."""
    path_str = str(md_path)
    current_hash = file_hash(path_str)

    if path_str in cache["posts"] and cache["posts"][path_str]["hash"] == current_hash:
        return False
    return True


def sync_writeup(md_path: Path, session: requests.Session, cache: dict, author_id: str = None) -> str:
    """Sync a single writeup to Ghost. Returns 'created', 'skipped', or 'failed'."""
    print(f"\n📄 Processing: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract metadata
    title = extract_title(content, md_path.stem)
    excerpt = extract_description(content)
    slug = slugify(title)
    tags = get_tags_for_path(md_path)

    print(f"  Title: {title}")
    print(f"  Slug: {slug}")

    # Check if post already exists on Ghost — skip if so
    if post_exists_on_ghost(session, slug):
        print(f"  ⊘ Already on Ghost, skipping")
        cache["posts"][str(md_path)] = {
            "hash": file_hash(str(md_path)),
            "slug": slug,
            "synced_at": datetime.now().isoformat(),
        }
        return "skipped"

    print(f"  Tags: {[t['name'] for t in tags]}")

    # Upload images and replace paths
    print("  Uploading images...")
    processed_content = process_images_in_markdown(content, md_path, session, cache)

    # Upload feature image
    feature_image_url = None
    feature_img_path = find_feature_image(md_path)
    if feature_img_path:
        feature_image_url = upload_image_to_ghost(session, feature_img_path, cache)

    # Convert to HTML
    html = markdown_to_ghost_html(processed_content)

    # Create post
    success = create_post(session, title, slug, html, excerpt, tags, feature_image_url, author_id)

    if success:
        cache["posts"][str(md_path)] = {
            "hash": file_hash(str(md_path)),
            "slug": slug,
            "synced_at": datetime.now().isoformat(),
        }
        return "created"

    return "failed"


def main():
    if not GHOST_ADMIN_KEY:
        print("❌ GHOST_ADMIN_API_KEY environment variable not set!")
        sys.exit(1)

    print("👻 Ghost Sync — Starting...")
    print(f"  Ghost URL: {GHOST_URL}")
    print(f"  Base dirs: {', '.join(BASE_DIRS)}")

    # Check for --force flag
    force_sync = "--force" in sys.argv

    # Load cache
    cache = load_cache()

    # Create authenticated session
    session = ghost_session(GHOST_ADMIN_KEY)

    # Test connection
    r = session.get(f"{GHOST_URL}/ghost/api/admin/site/")
    if r.status_code != 200:
        print(f"❌ Cannot connect to Ghost: {r.status_code}")
        sys.exit(1)
    print(f"  Connected to: {r.json()['site']['title']}")

    # Get owner user ID (required for integration post creation)
    owner_id = get_owner_id(session)

    # Discover writeups
    writeups = discover_writeups()
    print(f"\n📂 Found {len(writeups)} writeups")

    # Sync
    created = 0
    skipped_unchanged = 0
    skipped_exists = 0
    failed = 0

    for md_path in writeups:
        if not force_sync and not should_sync(md_path, cache):
            skipped_unchanged += 1
            continue

        result = sync_writeup(md_path, session, cache, owner_id)
        if result == "created":
            created += 1
        elif result == "skipped":
            skipped_exists += 1
        else:
            failed += 1

        # Save cache after each sync
        save_cache(cache)

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # Final cache save
    save_cache(cache)

    print(f"\n{'='*50}")
    print(f"✅ Sync complete!")
    print(f"  Created:  {created}")
    print(f"  Skipped:  {skipped_exists} (already on Ghost)")
    print(f"  Skipped:  {skipped_unchanged} (unchanged in repo)")
    print(f"  Failed:   {failed}")


if __name__ == "__main__":
    main()
