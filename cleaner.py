"""
URL cleaning + HTML-to-text cleaning using selectolax.

Constraints:
- Do NOT use requests
- Do NOT use BeautifulSoup
- Use selectolax.parser.HTMLParser
- Remove script, style, svg, img, nav, footer
- Extract visible text
- Normalize whitespace
- Limit output to first 8000 characters
"""

from __future__ import annotations

import re
from typing import Final
from urllib.parse import urlsplit, urlunsplit

from loguru import logger
from selectolax.parser import HTMLParser

from config.parameters import MAX_CHARS, STATS_PATH

_REMOVE_SELECTOR: Final[str] = "script,style,svg,img,nav,footer"


def build_stats_url(url: str) -> str:
    """
    Insert /prehled/stats/celkem/ into the URL path before the query string,
    preserving existing query parameters.

    Example:
    .../jablonec-CM8ySpMH/?mid=XYZ
    -> .../jablonec-CM8ySpMH/prehled/stats/celkem/?mid=XYZ
    """
    url = url.strip()
    if not url:
        raise ValueError("URL is empty.")

    parts = urlsplit(url)

    # Normalize path without trailing slash (so we can append reliably)
    path = parts.path.rstrip("/")

    # If already ends with stats path (with or without trailing slash), keep it
    if path.endswith(STATS_PATH.rstrip("/")):
        new_path = path + "/"
    else:
        new_path = f"{path}{STATS_PATH}"

    stats_url = urlunsplit(
        (parts.scheme, parts.netloc, new_path, parts.query, parts.fragment)
    )
    logger.debug(f"Built stats URL: {stats_url}")
    return stats_url


def normalize_match_url(url: str) -> str:
    """
    Normalize match URL a bit (mainly path trailing slash handling),
    but KEEP query parameters.
    """
    url = url.strip()
    if not url:
        raise ValueError("URL is empty.")

    parts = urlsplit(url)
    path = parts.path.rstrip("/") + "/"  # ensure trailing slash for the base match page
    normalized = urlunsplit(
        (parts.scheme, parts.netloc, path, parts.query, parts.fragment)
    )
    logger.debug(f"Normalized match URL: {normalized}")
    return normalized


def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace to single spaces and trim.
    """
    return re.sub(r"\s+", " ", text).strip()


def clean_html_to_text(html: str, max_chars: int = MAX_CHARS) -> str:
    """
    Parse and clean raw HTML and extract visible text.

    Steps:
    - Parse with selectolax HTMLParser
    - Remove tags: script, style, svg, img, nav, footer
    - Extract visible text from body
    - Normalize whitespace
    - Truncate to first max_chars

    Args:
        html: Raw HTML
        max_chars: Maximum length of returned text

    Returns:
        Cleaned text (<= max_chars)

    Raises:
        ValueError: If html is empty.
    """
    if not html or not html.strip():
        raise ValueError("HTML is empty.")

    parser = HTMLParser(html)
    logger.debug("Removing non-content elements...")
    for node in parser.css(_REMOVE_SELECTOR):
        node.decompose()

    logger.debug("Extracting text from body...")
    body = parser.body
    text = body.text(separator=" ") if body else parser.text(separator=" ")

    logger.debug("Normalizing whitespaces...")
    cleaned = _normalize_whitespace(text)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]

    return cleaned
