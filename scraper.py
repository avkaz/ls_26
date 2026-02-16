"""
Synchronous Playwright scraper for fetching fully-rendered HTML.

Requirements:
- playwright.sync_api
- headless Chromium
- slight scroll using page.mouse.wheel()
- brief wait for content load
- return raw HTML
- no async / no asyncio
"""

from __future__ import annotations

import os
import urllib.parse

from loguru import logger
from playwright.sync_api import Browser, Page, sync_playwright

from config.parameters import DEFAULT_TIMEOUT_MS


def fetch_html(url: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> str:
    """
    Fetch fully-rendered HTML from the given URL using synchronous Playwright.

    Args:
        url: Target URL.
        timeout_ms: Navigation timeout.

    Returns:
        Raw HTML content (page.content()).

    Raises:
        RuntimeError: If HTML could not be fetched.
    """
    if not url.strip():
        raise ValueError("URL is empty.")

    try:
        with sync_playwright() as p:
            env_proxy = os.getenv("PLAYWRIGHT_PROXY")
            proxy_to_use = env_proxy

            proxy_launch_arg = None
            if proxy_to_use:
                # Parse proxy URL into components
                parsed = urllib.parse.urlparse(proxy_to_use)
                server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                if parsed.username or parsed.password:
                    proxy_launch_arg = {
                        "server": server,
                        "username": urllib.parse.unquote(parsed.username)
                        if parsed.username
                        else None,
                        "password": urllib.parse.unquote(parsed.password)
                        if parsed.password
                        else None,
                    }
                else:
                    proxy_launch_arg = {"server": server}

            if proxy_launch_arg:
                browser: Browser = p.chromium.launch(
                    headless=True, proxy=proxy_launch_arg
                )
            else:
                browser: Browser = p.chromium.launch(headless=True)
            logger.info("Browser initialized.")
            page: Page = browser.new_page()

            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="domcontentloaded")
            logger.success("Page loaded successfully!")

            # Small scroll to trigger lazy-loaded content
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(3000)
            logger.debug("Page scrolled down.")

            html = page.content()
            browser.close()

            if not html or len(html) < 100:
                logger.error("Fetched HTML is empty or unexpectedly short.")
                raise RuntimeError("Fetched HTML is empty or unexpectedly short.")
            else:
                logger.info("HTML content loaded successfully.")

            return html
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch HTML via Playwright: {exc}") from exc
