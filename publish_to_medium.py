#!/usr/bin/env python3
"""
Medium Publisher for CTF Writeups
Publishes Obsidian Markdown files to Medium as drafts.

Features:
- Frontmatter support for selective publishing
- Tracking via published_posts.json (prevents duplicates)
- Content change detection via MD5 hash
- Interactive prompts for updates
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import markdown2
import yaml


# ============== CONFIGURATION ==============
# Environment variables override defaults
MEDIUM_API_TOKEN = os.getenv('MEDIUM_TOKEN', "")
GITHUB_PAGES_URL = os.getenv('GITHUB_PAGES_URL', "https://onurcangnc.github.io/ctf_writeups")
BASE_DIR = './TryHackMe'
TRACKING_FILE = 'published_posts.json'
# ===========================================


class PublishedPostsTracker:
    """Manages tracking of published posts."""

    def __init__(self, tracking_file: str):
        self.tracking_file = Path(tracking_file)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load tracking data from file."""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save(self):
        """Save tracking data to file."""
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, post_name: str) -> Optional[Dict[str, Any]]:
        """Get tracking data for a post."""
        return self.data.get(post_name)

    def is_published(self, post_name: str) -> bool:
        """Check if a post has been published."""
        return post_name in self.data

    def has_changed(self, post_name: str, content: str) -> bool:
        """Check if content has changed since last publish."""
        if post_name not in self.data:
            return True
        return self.data[post_name].get('content_hash') != self._hash_content(content)

    def _hash_content(self, content: str) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def update(self, post_name: str, medium_id: str, medium_url: str, content: str):
        """Update tracking data for a post."""
        self.data[post_name] = {
            'medium_id': medium_id,
            'medium_url': medium_url,
            'published_at': datetime.now(timezone.utc).isoformat(),
            'content_hash': self._hash_content(content)
        }
        self.save()

    def remove(self, post_name: str):
        """Remove a post from tracking."""
        if post_name in self.data:
            del self.data[post_name]
            self.save()


class MediumPublisher:
    """Handles communication with Medium API."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.user_id = None

    def connect(self) -> bool:
        """Connect to Medium API and get user ID."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get("https://api.medium.com/v1/me", headers=headers)
            response.raise_for_status()
            self.user_id = response.json()["data"]["id"]
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Failed to connect to Medium API: {e}")
            return False

    def create_draft(self, title: str, content: str, tags: list = None) -> Optional[Dict]:
        """Create a new draft post on Medium."""
        if tags is None:
            tags = ["CTF", "CyberSecurity", "Writeup", "TryHackMe"]

        url = f"https://api.medium.com/v1/users/{self.user_id}/posts"

        payload = {
            "title": title,
            "contentFormat": "html",
            "content": content,
            "tags": tags[:5],  # Medium allows max 5 tags
            "publishStatus": "draft"
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            print(f"  ERROR: {e}")
            if e.response and e.response.json():
                print(f"  Details: {e.response.json()}")
            return None


class MarkdownProcessor:
    """Processes Markdown files for Medium publishing."""

    def __init__(self, github_pages_url: str):
        self.github_pages_url = github_pages_url

    def parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """
        Parse YAML frontmatter from markdown.
        Returns (frontmatter_dict, content_without_frontmatter).
        """
        if not content.startswith('---'):
            return {}, content

        # Find the end of frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            if frontmatter is None:
                frontmatter = {}
            content_without = parts[2].lstrip('\n')
            return frontmatter, content_without
        except yaml.YAMLError:
            return {}, content

    def should_publish(self, frontmatter: Dict) -> bool:
        """Check if post should be published based on frontmatter."""
        return frontmatter.get('publish-medium', False) is True

    def get_title(self, frontmatter: Dict, content: str, filename: str) -> str:
        """Extract title from frontmatter or markdown content."""
        # First check frontmatter
        if 'title' in frontmatter:
            return frontmatter['title']

        # Try to find first H1 in markdown
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        # Fallback to filename
        return Path(filename).stem.replace('-', ' ').replace('_', ' ').title()

    def get_tags(self, frontmatter: Dict) -> list:
        """Get tags from frontmatter."""
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        if not tags:
            tags = ["CTF", "CyberSecurity", "Writeup", "TryHackMe"]
        return tags[:5]  # Max 5 tags

    def replace_obsidian_links(self, content: str, dir_name: str) -> str:
        """
        Replace Obsidian image links ![[...]] with HTML img tags
        pointing to GitHub Pages.
        """
        obsidian_pattern = r'!\[\[(.*?)\]\]'

        def replace_link(match):
            image_path = match.group(1)
            filename = os.path.basename(image_path)
            full_url = f"{self.github_pages_url}/TryHackMe/{dir_name}/images/{filename}"
            return f'<img src="{full_url}" alt="{filename}">'

        return re.sub(obsidian_pattern, replace_link, content)

    def to_html(self, content: str) -> str:
        """Convert markdown to HTML."""
        return markdown2.markdown(
            content,
            extras=['fenced-code-blocks', 'code-friendly', 'header-ids']
        )

    def process(self, markdown_content: str, dir_name: str, filename: str) -> Dict:
        """
        Process markdown file and return dict with title, content, tags, etc.
        """
        frontmatter, content = self.parse_frontmatter(markdown_content)

        return {
            'should_publish': self.should_publish(frontmatter),
            'title': self.get_title(frontmatter, content, filename),
            'tags': self.get_tags(frontmatter),
            'html': f"<h1>{self.get_title(frontmatter, content, filename)}</h1>" +
                   self.to_html(self.replace_obsidian_links(content, dir_name)),
            'frontmatter': frontmatter,
            'content': content  # For hashing
        }


class PromptHandler:
    """Handles user prompts for interactive decisions."""

    @staticmethod
    def ask_update(post_name: str, tracked_data: Dict) -> str:
        """Ask user what to do with changed content."""
        published_date = tracked_data.get('published_at', 'unknown')[:10]
        print(f"\n{'='*50}")
        print(f"'{post_name}' zaten gönderilmiş ({published_date}).")
        print("İçerik değişmiş.")
        print('='*50)

        while True:
            choice = input("[y] Yeni draft oluştur   [n] Atla   [v] Farkları göster: ").lower().strip()
            if choice in ['y', 'n', 'v']:
                return choice
            print("Geçersiz seçim. y, n veya v girin.")

    @staticmethod
    def show_diff(old_hash: str, new_hash: str):
        """Show that content has changed (hash comparison)."""
        print(f"\nEski hash: {old_hash[:16]}...")
        print(f"Yeni hash: {new_hash[:16]}...")
        print("İçerik değişmiş.")

    @staticmethod
    def ask_confirm(posts_to_publish: list) -> bool:
        """Ask for confirmation before publishing."""
        print(f"\n{len(posts_to_publish)} yazı gönderilecek:")
        for post in posts_to_publish:
            print(f"  - {post}")
        return input("\nDevam etmek istiyor musunuz? [y/N]: ").lower().strip() == 'y'


def process_markdown_file(md_file: Path, dir_name: str, processor: MarkdownProcessor,
                          tracker: PublishedPostsTracker, publisher: MediumPublisher,
                          prompt_handler: PromptHandler, auto_mode: bool = False) -> bool:
    """
    Process a single markdown file and publish to Medium if needed.
    Returns True if published/skipped successfully, False on error.
    """
    print(f"\n  İşleniyor: {md_file.name}")

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Process markdown
    result = processor.process(markdown_content, dir_name, md_file.name)

    # Check if should publish
    if not result['should_publish']:
        print(f"  → Atlandı (publish-medium: true yok)")
        return True

    title = result['title']
    content = result['content']

    # Check if already published
    if tracker.is_published(dir_name):
        tracked_data = tracker.get(dir_name)

        # Check if content changed
        if not tracker.has_changed(dir_name, content):
            print(f"  → Atlandı (Zaten gönderilmiş, içerik aynı)")
            print(f"     URL: {tracked_data.get('medium_url', 'N/A')}")
            return True

        # Content changed - ask what to do
        print(f"  → İçerik değişmiş!")
        print(f"     Eski draft: {tracked_data.get('medium_url', 'N/A')}")

        if auto_mode:
            # In auto mode, skip updates
            print(f"  → Atlandı (Auto mode: güncelleme yapılmaz)")
            return True

        choice = prompt_handler.ask_update(title, tracked_data)

        if choice == 'n':
            print(f"  → Atlandı")
            return True
        elif choice == 'v':
            prompt_handler.show_diff(tracked_data['content_hash'],
                                    tracker._hash_content(content))
            choice = input("[y] Yeni draft oluştur   [n] Atla: ").lower().strip()
            if choice != 'y':
                print(f"  → Atlandı")
                return True

        # User chose to create new draft
        print(f"  → Yeni draft oluşturuluyor...")

    # Publish to Medium
    medium_result = publisher.create_draft(title, result['html'], result['tags'])

    if medium_result:
        tracker.update(dir_name, medium_result['id'], medium_result['url'], content)
        print(f"  ✓ SUCCESS: Draft oluşturuldu!")
        print(f"     URL: {medium_result['url']}")
        return True
    else:
        print(f"  ✗ FAILED: Gönderilemedi")
        return False


def main(auto_mode: bool = False):
    """Main entry point."""
    print("=" * 50)
    print("CTF Writeups - Medium Publisher v2.0")
    print("=" * 50)

    # Initialize components
    tracker = PublishedPostsTracker(TRACKING_FILE)
    publisher = MediumPublisher(MEDIUM_API_TOKEN)
    processor = MarkdownProcessor(GITHUB_PAGES_URL)
    prompt_handler = PromptHandler()

    # Connect to Medium
    print("\nMedium API'ye bağlanılıyor...")
    if not publisher.connect():
        print("Bağlantı başarısız. Token'ı kontrol edin.")
        return

    print(f"Bağlandı: User ID = {publisher.user_id}")

    # Find markdown files
    base_path = Path(BASE_DIR)
    if not base_path.exists():
        print(f"Hata: '{BASE_DIR}' dizini bulunamadı.")
        return

    directories = [d for d in base_path.iterdir() if d.is_dir()]

    # Find all publishable posts
    publishable = []
    for directory in directories:
        md_files = list(directory.glob("*.md"))
        for md_file in md_files:
            if md_file.name.lower() in ["readme.md", "tryhackme.md"]:
                continue

            # Quick check for frontmatter
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                frontmatter, _ = processor.parse_frontmatter(content)
                if processor.should_publish(frontmatter):
                    post_name = directory.name
                    # Check if new or changed
                    if not tracker.is_published(post_name) or tracker.has_changed(post_name, content):
                        publishable.append((directory, md_file))

    if not publishable:
        print("\nYeni veya değişmiş publish-medium: true yazı bulunamadı.")
        return

    print(f"\n{len(publishable)} adet publishable yazı bulundu:")
    for directory, md_file in publishable:
        is_new = not tracker.is_published(directory.name)
        status = "YENİ" if is_new else "DEĞİŞMİŞ"
        print(f"  [{status}] {directory.name}")

    if not auto_mode:
        if not prompt_handler.ask_confirm([d.name for d, _ in publishable]):
            print("İptal edildi.")
            return

    # Process each file
    success_count = 0
    for directory, md_file in publishable:
        print(f"\n{'=' * 50}")
        print(f"Dizin: {directory.name}")
        print('=' * 50)

        if process_markdown_file(md_file, directory.name, processor, tracker,
                                 publisher, prompt_handler, auto_mode):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"Tamamlandı! {success_count}/{len(publishable)} işlem başarılı.")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Publish CTF writeups to Medium')
    parser.add_argument('--auto', action='store_true',
                       help='Auto mode (no prompts, skip updates)')

    args = parser.parse_args()
    main(auto_mode=args.auto)
