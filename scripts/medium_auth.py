#!/usr/bin/env python3
"""
Medium Authentication with 2FA support
Uses Playwright for login and Gmail API for 2FA code
"""

import os
import re
import json
import asyncio
from datetime import datetime, timedelta

from playwright.async_api import async_playwright


class MediumAuth:
    """Handle Medium authentication with 2FA"""

    def __init__(self):
        self.email = os.environ.get('MEDIUM_EMAIL')
        self.password = os.environ.get('MEDIUM_PASSWORD')
        self.gmail_api_key = os.environ.get('GMAIL_API_KEY')

    async def get_2fa_code_from_gmail(self) -> str:
        """Get 2FA code from Gmail using API"""

        # Google OAuth 2.0 flow needed for Gmail API
        # This requires:
        # 1. Google Cloud project with Gmail API enabled
        # 2. OAuth 2.0 credentials (client_id, client_secret)
        # 3. Refresh token stored in secrets

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=os.environ.get('GMAIL_REFRESH_TOKEN'),
            client_id=os.environ.get('GMAIL_CLIENT_ID'),
            client_secret=os.environ.get('GMAIL_CLIENT_SECRET'),
            token_uri='https://oauth2.googleapis.com/token'
        )

        service = build('gmail', 'v1', credentials=creds)

        # Search for recent Medium email
        # Time filter for emails from last 5 minutes
        time_filter = datetime.utcnow() - timedelta(minutes=5)
        query = f"from:Medium after:{int(time_filter.timestamp())}"

        results = service.users().messages().list(
            userId='me',
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return None

        # Get the most recent message
        msg_id = messages[0]['id']
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()

        # Extract email body
        import base64
        for part in message['payload'].get('parts', []):
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')

                # Extract 6-digit code
                match = re.search(r'\b(\d{6})\b', body)
                if match:
                    return match.group(1)

        return None

    async def login_and_get_cookies(self) -> list:
        """Login to Medium and return cookies"""

        if not self.email or not self.password:
            raise ValueError("MEDIUM_EMAIL and MEDIUM_PASSWORD required")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Go to Medium signin
            await page.goto('https://medium.com/m/signin')

            # Wait for signin page
            await page.wait_for_load_state('networkidle')

            # Click sign in with email (if needed)
            try:
                email_btn = page.get_by_text('Sign in with email')
                if await email_btn.is_visible():
                    await email_btn.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            # Enter email
            await page.fill('input[type="email"]', self.email)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(2000)

            # Enter password
            await page.fill('input[type="password"]', self.password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)

            # Check if 2FA is required
            code_input = None
            try:
                code_input = page.locator('input[type="text"], input[placeholder*="code"]')
                if await code_input.is_visible():
                    # Get 2FA code from Gmail
                    code = await self.get_2fa_code_from_gmail()

                    if not code:
                        raise ValueError("Could not get 2FA code from Gmail")

                    await code_input.fill(code)
                    await page.click('button[type="submit"]')
                    await page.wait_for_timeout(3000)
            except:
                pass

            # Wait for login to complete
            await page.wait_for_url('**/me/**', timeout=10000)
            await page.wait_for_timeout(2000)

            # Get cookies
            cookies = await context.cookies()
            await browser.close()

            return cookies

    def format_cookies_for_export(self, cookies: list) -> list:
        """Format cookies for EditThisCookie format"""
        formatted = []
        for cookie in cookies:
            formatted.append({
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie.get('domain', '.medium.com'),
                'path': cookie.get('path', '/'),
                'expirationDate': cookie.get('expires', 9999999999),
                'secure': cookie.get('secure', True),
                'httpOnly': cookie.get('httpOnly', False),
                'sameSite': cookie.get('sameSite', 'Lax')
            })
        return formatted


async def main():
    """Main entry point"""
    auth = MediumAuth()

    print("Logging in to Medium...")
    cookies = await auth.login_and_get_cookies()

    # Format and output cookies
    formatted = auth.format_cookies_for_export(cookies)

    # Save to file (for GitHub Actions)
    with open('.medium_cookies.json', 'w') as f:
        json.dump(formatted, f, indent=2)

    print(f"✓ Saved {len(formatted)} cookies to .medium_cookies.json")

    # Also output to GitHub Actions (masked)
    cookies_json = json.dumps(formatted)
    print(f"::set-output name=cookies::{cookies_json}")

    return formatted


if __name__ == '__main__':
    asyncio.run(main())
