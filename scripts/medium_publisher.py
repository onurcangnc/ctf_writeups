#!/usr/bin/env python3
"""
Medium Publisher Library
Publish markdown to Medium using API only (no headless browser).
"""

import os
import json
import time
import re
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    url: Optional[str] = None
    post_id: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None


class MediumPublisher:
    """Medium Publisher - Create drafts via API."""

    BASE_URL = "https://medium.com"

    def __init__(self, cookies: Optional[List[dict]] = None):
        """
        Initialize publisher with Medium cookies.

        Args:
            cookies: List of cookies from browser (EditThisCookie format)
        """
        self.cookies = cookies or self._load_cookies()
        self.session = None

    def _load_cookies(self) -> Optional[List[dict]]:
        """Load cookies from .medium_cookies.json file."""
        cookie_file = Path('.medium_cookies.json')
        if cookie_file.exists():
            try:
                return json.loads(cookie_file.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return None

    @property
    def cookie_dict(self) -> Dict[str, str]:
        """Cookies as dict for requests."""
        return {c['name']: c['value'] for c in self.cookies if 'name' in c and 'value' in c}

    @property
    def xsrf_token(self) -> Optional[str]:
        """Get XSRF token from cookies."""
        return next((c.get('value') for c in self.cookies if c.get('name') == 'xsrf'), None)

    def _build_headers(self) -> dict:
        """Build request headers with XSRF token."""
        timestamp = int(time.time() * 1000)
        return {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': self.BASE_URL,
            'referer': f'{self.BASE_URL}/new-story',
            'sec-ch-ua': '"Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-obvious-cid': 'web',
            'x-xsrf-token': self.xsrf_token or '',
            'x-client-date': str(timestamp),
        }

    def _parse_jsonp(self, text: str) -> dict:
        """Parse Medium's JSONP-wrapped JSON responses."""
        text = text.strip()
        if text.startswith(')]}'):
            json_start = text.find('{')
            if json_start > 0:
                text = text[json_start:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def extract_title(self, content: str, filename: str) -> str:
        """Extract title from markdown content or filename."""
        content_without_code = re.sub(r'```[\s\S]*?```', '', content)
        match = re.search(r'^#\s+(.+)$', content_without_code, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()

    def prepare_markdown(self, content: str) -> str:
        """Convert Obsidian markdown to Medium-compatible format."""
        # Remove image links
        content = re.sub(r'!\[\[(.*?)\]\]', '', content)
        # Remove wiki links - [[link]] and [[link|alias]]
        content = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', content)
        content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', content)
        # Normalize newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()

    def publish(self, md_path: str) -> PublishResult:
        """
        Publish markdown to Medium as draft.

        Args:
            md_path: Path to markdown file

        Returns:
            PublishResult with status and URL
        """
        if not HAS_CURL_CFFI:
            return PublishResult(success=False, error='curl_cffi not installed. Run: pip install curl-cffi')

        if not self.xsrf_token:
            return PublishResult(success=False, error='No XSRF token in cookies')

        md_file = Path(md_path)
        if not md_file.exists():
            return PublishResult(success=False, error='File not found')

        content = md_file.read_text(encoding='utf-8')
        title = self.extract_title(content, md_file.name)
        markdown = self.prepare_markdown(content)

        # Create session
        self.session = curl_requests.Session(impersonate="chrome124")

        # Create draft
        response = self.session.post(
            f'{self.BASE_URL}/new-story?logLockId={int(time.time() * 1000)}',
            headers=self._build_headers(),
            cookies=self.cookie_dict,
            json={"deltas": [], "baseRev": -1, "coverless": True, "visibility": 0},
            timeout=30
        )

        if response.status_code not in [200, 201]:
            return PublishResult(
                success=False,
                error=f'Create failed: {response.status_code} - {response.text[:200]}',
            )

        # Extract post ID
        data = self._parse_jsonp(response.text)
        post_id = None

        if 'payload' in data and isinstance(data['payload'], dict):
            if 'value' in data['payload']:
                post_id = data['payload']['value'].get('id')
        elif 'id' in data:
            post_id = data['id']

        if not post_id:
            match = re.search(r'([a-f0-9]{12,})', response.text)
            if match:
                post_id = match.group(1)

        if post_id:
            # Upload content via API
            self._upload_content(post_id, title, markdown)
            return PublishResult(
                success=True,
                post_id=post_id,
                url=f'{self.BASE_URL}/p/{post_id}/edit',
                title=title
            )

        return PublishResult(success=False, error='Could not extract post ID')

    def _upload_content(self, post_id: str, title: str, content: str) -> bool:
        """Upload content to draft via API."""
        try:
            # Build content deltas for Medium API
            deltas = [
                {
                    "type": "paragraph",
                    "content": [title],
                    "markup": [[0, {"type": "strong"}]],
                },
                {"type": "hr"},
            ]

            # Split content into paragraphs
            paragraphs = re.split(r'\n\n+', content)
            for para in paragraphs:
                if para.strip():
                    deltas.append({
                        "type": "paragraph",
                        "content": [para.strip()]
                    })

            response = self.session.post(
                f'{self.BASE_URL}/p/{post_id}?logLockId={int(time.time() * 1000)}',
                headers=self._build_headers(),
                cookies=self.cookie_dict,
                json={
                    "deltas": deltas,
                    "baseRev": -1,
                    "coverless": True,
                    "visibility": 0
                },
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception:
            return False


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Medium Publisher Library')
    parser.add_argument('file', help='Markdown file to publish')

    args = parser.parse_args()

    publisher = MediumPublisher()
    result = publisher.publish(args.file)

    if result.success:
        print(f"✓ Draft created: {result.url}")
    else:
        print(f"✗ Failed: {result.error}")
