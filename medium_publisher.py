#!/usr/bin/env python3
"""
Medium Publisher Library
Reusable library for publishing markdown to Medium.
"""

import os
import json
import time
import re
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    url: Optional[str] = None
    post_id: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    method: Optional[str] = None  # 'api', 'playwright', 'clipboard'


class MediumPublisher:
    """Medium Publisher - Create drafts and publish content."""

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
            # Return empty dict on parse error
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

    def create_draft(self, title: str) -> Optional[PublishResult]:
        """
        Create a new draft post via API.

        Args:
            title: Title for the draft

        Returns:
            PublishResult with post_id and URL if successful
        """
        if not HAS_CURL_CFFI:
            return PublishResult(success=False, error='curl_cffi not installed')

        if not self.xsrf_token:
            return PublishResult(success=False, error='No XSRF token in cookies')

        self.session = curl_requests.Session(impersonate="chrome124")

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
                error=f'Create failed: {response.status_code}',
            )

        # Extract post ID
        try:
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
                return PublishResult(
                    success=True,
                    post_id=post_id,
                    url=f'{self.BASE_URL}/p/{post_id}/edit',
                    title=title,
                    method='api'
                )
        except Exception as e:
            return PublishResult(success=False, error=f'Parse error: {e}')

        return PublishResult(success=False, error='Could not extract post ID')

    async def publish_via_playwright(
        self,
        post_id: str,
        markdown_content: str,
        title: str
    ) -> PublishResult:
        """
        Publish content using Playwright browser automation.

        Args:
            post_id: Medium post ID
            markdown_content: Markdown content to publish
            title: Post title

        Returns:
            PublishResult indicating success/failure
        """
        if not HAS_PLAYWRIGHT:
            return PublishResult(success=False, error='Playwright not installed')

        # Format cookies for Playwright
        playwright_cookies = []
        for c in self.cookies:
            sameSite_raw = c.get('sameSite', 'Lax')
            if isinstance(sameSite_raw, str):
                sameSite = sameSite_raw.capitalize()
                if sameSite not in ['Strict', 'Lax', 'None']:
                    sameSite = 'Lax'
            else:
                sameSite = 'Lax'

            playwright_cookies.append({
                'name': c.get('name', ''),
                'value': c.get('value', ''),
                'domain': c.get('domain', '.medium.com'),
                'path': c.get('path', '/'),
                'secure': c.get('secure', True),
                'httpOnly': c.get('httpOnly', False),
                'sameSite': sameSite
            })

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, channel="chrome")
            context = await browser.new_context()
            page = await context.new_page()

            # Set cookies
            await page.goto('https://medium.com/', timeout=15000)
            await context.add_cookies(playwright_cookies)

            # Open editor
            await page.goto(
                f'{self.BASE_URL}/p/{post_id}/edit',
                wait_until='domcontentloaded',
                timeout=30000
            )
            await asyncio.sleep(2)

            # Type content
            full_content = f"# {title}\n\n{markdown_content}"
            await page.click('body', timeout=5000)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Delete')

            lines = full_content.split('\n')
            for i, line in enumerate(lines):
                await page.keyboard.type(line)
                if i < len(lines) - 1:
                    await page.keyboard.press('Enter')
                await asyncio.sleep(0.01)

            # Save
            await asyncio.sleep(2)
            await page.keyboard.press('Control+S')
            await asyncio.sleep(3)

            await browser.close()

        return PublishResult(
            success=True,
            post_id=post_id,
            url=f'{self.BASE_URL}/p/{post_id}/edit',
            title=title,
            method='playwright'
        )

    def publish_to_clipboard(self, markdown_content: str, title: str) -> PublishResult:
        """
        Copy formatted markdown to clipboard for manual pasting.

        Args:
            markdown_content: Markdown content
            title: Post title

        Returns:
            PublishResult indicating clipboard operation
        """
        full_content = f"# {title}\n\n{markdown_content}"

        try:
            import pyperclip
            pyperclip.copy(full_content)
            return PublishResult(
                success=True,
                method='clipboard',
                title=title
            )
        except ImportError:
            # Windows fallback
            try:
                import subprocess
                subprocess.run(
                    ['clip'],
                    input=full_content.encode('utf-16'),
                    check=True,
                    shell=True
                )
                return PublishResult(
                    success=True,
                    method='clipboard',
                    title=title
                )
            except:
                return PublishResult(
                    success=False,
                    error='Could not copy to clipboard',
                    method='clipboard'
                )

    async def publish_async(
        self,
        md_path: str,
        method: str = 'auto'
    ) -> PublishResult:
        """
        Publish markdown to Medium.

        Args:
            md_path: Path to markdown file
            method: 'auto', 'playwright', or 'clipboard'

        Returns:
            PublishResult with status and URL
        """
        md_file = Path(md_path)
        if not md_file.exists():
            return PublishResult(success=False, error='File not found')

        content = md_file.read_text(encoding='utf-8')
        title = self.extract_title(content, md_file.name)
        markdown = self.prepare_markdown(content)

        # Step 1: Create draft
        draft_result = self.create_draft(title)
        if not draft_result.success:
            return draft_result

        post_id = draft_result.post_id

        # Step 2: Publish content
        if method == 'auto':
            # Try Playwright first, fallback to clipboard
            if HAS_PLAYWRIGHT:
                result = await self.publish_via_playwright(post_id, markdown, title)
                if result.success:
                    return result
            return self.publish_to_clipboard(markdown, title)

        elif method == 'playwright':
            if not HAS_PLAYWRIGHT:
                return PublishResult(success=False, error='Playwright not installed')
            return await self.publish_via_playwright(post_id, markdown, title)

        else:  # clipboard
            return self.publish_to_clipboard(markdown, title)

    def publish(self, md_path: str, method: str = 'auto') -> PublishResult:
        """Sync wrapper for publish_async."""
        return asyncio.run(self.publish_async(md_path, method))


def publish(md_path: str, cookies: Optional[List[dict]] = None, method: str = 'auto') -> PublishResult:
    """
    Convenience function to publish markdown to Medium.

    Args:
        md_path: Path to markdown file
        cookies: Optional Medium cookies (defaults to .medium_cookies.json)
        method: 'auto', 'playwright', or 'clipboard'

    Returns:
        PublishResult with status and URL
    """
    publisher = MediumPublisher(cookies)
    return publisher.publish(md_path, method)


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Medium Publisher Library')
    parser.add_argument('file', help='Markdown file to publish')
    parser.add_argument('--method', choices=['auto', 'playwright', 'clipboard'],
                       default='auto', help='Publishing method')

    args = parser.parse_args()

    result = publish(args.file, method=args.method)

    if result.success:
        print(f"✓ Published: {result.url}")
    else:
        print(f"✗ Failed: {result.error}")
