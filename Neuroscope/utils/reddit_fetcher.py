"""
Reddit discussion fetcher for NeuroScope.

Uses Playwright (headless Chromium) to render public Reddit posts in a browser,
extract post metadata and visible comments from the live DOM, and return the same
shapes expected by the rest of the application.

Reddit blocks anonymous .json endpoints (HTTP 403). Browser rendering is required.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import (
        Error as PlaywrightError,
        TimeoutError as PlaywrightTimeoutError,
        sync_playwright,
    )
except ImportError as exc:  # pragma: no cover - runtime dependency check
    sync_playwright = None  # type: ignore[assignment,misc]
    PlaywrightError = Exception  # type: ignore[assignment,misc]
    PlaywrightTimeoutError = Exception  # type: ignore[assignment,misc]
    _PLAYWRIGHT_IMPORT_ERROR = exc
else:
    _PLAYWRIGHT_IMPORT_ERROR = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_LIMIT = 200
MAX_LIMIT = 500
CACHE_TTL_SECONDS = 300
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0

PAGE_LOAD_TIMEOUT_MS = 90_000
SELECTOR_TIMEOUT_MS = 30_000
ACTION_TIMEOUT_MS = 5_000

MAX_SCROLL_ROUNDS = 40
SCROLL_PAUSE_MS = 1_200
STALL_ROUNDS_BEFORE_STOP = 4

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

VIEWPORT = {"width": 1366, "height": 900}

_COOKIE_BUTTONS = (
    "Accept all",
    "Accept All",
    "Reject optional",
    "Reject Optional",
    "Accept cookies",
)

_DISMISS_BUTTONS = (
    "Not now",
    "Continue",
    "No thanks",
    "Maybe later",
)

_LOAD_MORE_PATTERNS = (
    re.compile(r"view more comments", re.I),
    re.compile(r"show more replies", re.I),
    re.compile(r"\d+\s+more replies", re.I),
)


@dataclass
class _CacheEntry:
    metadata: dict[str, Any]
    comments: list[str]
    limit: int
    include_replies: bool
    timestamp: float


_url_cache: dict[str, _CacheEntry] = {}


# ---------------------------------------------------------------------------
# URL normalization
# ---------------------------------------------------------------------------

def normalize_reddit_url(reddit_url: str) -> str:
    reddit_url = reddit_url.strip()

    parsed = urlparse(reddit_url)

    if parsed.netloc.endswith("redd.it"):
        raise ValueError(
            "Short redd.it URLs are not currently supported. "
            "Please paste the full Reddit URL."
        )

    if "reddit.com" not in parsed.netloc:
        raise ValueError("Invalid Reddit URL")

    return urlunparse(
        (
            parsed.scheme or "https",
            parsed.netloc,
            parsed.path.rstrip("/"),
            "",
            "",
            "",
        )
    )


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _cache_get(clean_url: str) -> _CacheEntry | None:
    entry = _url_cache.get(clean_url)
    if entry is None:
        return None
    if time.time() - entry.timestamp > CACHE_TTL_SECONDS:
        _url_cache.pop(clean_url, None)
        return None
    return entry


def _cache_set(
    clean_url: str,
    metadata: dict[str, Any],
    comments: list[str],
    limit: int,
    include_replies: bool,
) -> None:
    _url_cache[clean_url] = _CacheEntry(
        metadata=metadata,
        comments=comments,
        limit=limit,
        include_replies=include_replies,
        timestamp=time.time(),
    )


def _cache_covers(entry: _CacheEntry, limit: int, include_replies: bool) -> bool:
    if entry.limit < limit:
        return False
    if include_replies and not entry.include_replies:
        return False
    return True


def _filter_comments(comments: list[str], include_replies: bool, limit: int) -> list[str]:
    return comments[:limit]


# ---------------------------------------------------------------------------
# Playwright helpers
# ---------------------------------------------------------------------------

def _require_playwright() -> None:
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright is required for Reddit fetching but is not installed.\n\n"
            "Install it with:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium\n\n"
            f"Import error: {_PLAYWRIGHT_IMPORT_ERROR}"
        )


def _parse_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def _normalize_subreddit(raw: str | None) -> str:
    if not raw:
        return ""
    text = raw.strip()
    if text.lower().startswith("r/"):
        return text[2:]
    return text


def _dismiss_overlays(page) -> None:
    for label in _COOKIE_BUTTONS:
        try:
            button = page.get_by_role("button", name=label).first
            if button.is_visible(timeout=800):
                button.click(timeout=ACTION_TIMEOUT_MS)
                page.wait_for_timeout(400)
        except (PlaywrightError, PlaywrightTimeoutError):
            continue

    for label in _DISMISS_BUTTONS:
        try:
            button = page.get_by_role("button", name=label).first
            if button.is_visible(timeout=500):
                button.click(timeout=ACTION_TIMEOUT_MS)
                page.wait_for_timeout(300)
        except (PlaywrightError, PlaywrightTimeoutError):
            continue

    for label in ("Close", "Dismiss"):
        try:
            button = page.get_by_role("button", name=label).first
            if button.is_visible(timeout=400):
                button.click(timeout=ACTION_TIMEOUT_MS)
                page.wait_for_timeout(300)
        except (PlaywrightError, PlaywrightTimeoutError):
            continue


def _wait_for_post(page) -> None:
    page.locator("shreddit-post").first.wait_for(
        state="attached",
        timeout=SELECTOR_TIMEOUT_MS,
    )


def _click_load_more_buttons(page) -> None:
    try:
        buttons = page.get_by_role("button")
        count = buttons.count()
    except PlaywrightError:
        return

    for index in range(min(count, 40)):
        try:
            button = buttons.nth(index)
            if not button.is_visible(timeout=200):
                continue
            name = (button.get_attribute("aria-label") or button.inner_text(timeout=300) or "").strip()
            if not name:
                continue
            if any(pattern.search(name) for pattern in _LOAD_MORE_PATTERNS):
                button.click(timeout=ACTION_TIMEOUT_MS)
                page.wait_for_timeout(350)
        except (PlaywrightError, PlaywrightTimeoutError):
            continue


def _scroll_comment_section(page, target_count: int, include_replies: bool) -> None:
    stall_rounds = 0
    previous_count = 0

    for _ in range(MAX_SCROLL_ROUNDS):
        page.evaluate(
            """
            () => {
                const commentRegion =
                    document.querySelector('[aria-label="Comments"]') ||
                    document.querySelector('shreddit-comment-tree') ||
                    document.body;
                commentRegion.scrollIntoView({ block: 'end' });
                window.scrollTo(0, document.body.scrollHeight);
            }
            """
        )
        page.wait_for_timeout(SCROLL_PAUSE_MS)
        _click_load_more_buttons(page)

        current_count = page.evaluate(
            """
            (includeReplies) => {
                const nodes = [...document.querySelectorAll('shreddit-comment')];
                if (includeReplies) return nodes.length;
                return nodes.filter((node) => node.getAttribute('depth') === '0').length;
            }
            """,
            include_replies,
        )

        if current_count >= target_count:
            return

        if current_count <= previous_count:
            stall_rounds += 1
        else:
            stall_rounds = 0

        if stall_rounds >= STALL_ROUNDS_BEFORE_STOP:
            return

        previous_count = current_count


_EXTRACT_PAGE_DATA_JS = """
(includeReplies) => {
    const cleanText = (value) => (value || "").replace(/\\s+/g, " ").trim();

    const getCommentBody = (node) => {
        const slot = node.querySelector('[slot="comment"]');
        if (slot) {
            const text = cleanText(slot.innerText);
            if (text) return text;
        }

        const paragraphs = [...node.querySelectorAll("p")].map((p) => cleanText(p.innerText)).filter(Boolean);
        if (paragraphs.length) {
            return paragraphs.join("\\n");
        }

        return cleanText(node.innerText);
    };

    const post = document.querySelector("shreddit-post");
    if (!post) {
        return { error: "Post content did not load. Reddit may be blocking automated access." };
    }

    const metadata = {
        title: cleanText(post.getAttribute("post-title") || document.querySelector("h1")?.innerText),
        subreddit: (post.getAttribute("subreddit-prefixed-name") || "").replace(/^r\\//i, ""),
        author: cleanText(post.getAttribute("author")),
        score: Number.parseInt(post.getAttribute("score") || "0", 10) || 0,
        num_comments: Number.parseInt(post.getAttribute("comment-count") || "0", 10) || 0,
    };

    const seen = new Set();
    const comments = [];

    for (const node of document.querySelectorAll("shreddit-comment")) {
        const depth = node.getAttribute("depth") || "0";
        if (!includeReplies && depth !== "0") {
            continue;
        }

        const body = getCommentBody(node);
        if (!body) {
            continue;
        }

        const key = node.getAttribute("thingid") || `${depth}:${body.slice(0, 120)}`;
        if (seen.has(key)) {
            continue;
        }
        seen.add(key);
        comments.push(body);
    }

    return { metadata, comments };
}
"""


def _extract_page_data(page, include_replies: bool) -> tuple[dict[str, Any], list[str]]:
    payload = page.evaluate(_EXTRACT_PAGE_DATA_JS, include_replies)

    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected Reddit page extraction result.")

    if payload.get("error"):
        raise RuntimeError(str(payload["error"]))

    metadata = payload.get("metadata") or {}
    comments = payload.get("comments") or []

    if not metadata.get("title"):
        raise RuntimeError(
            "Could not extract Reddit post metadata. "
            "The page may not have finished loading."
        )

    return {
        "title": metadata.get("title", ""),
        "subreddit": _normalize_subreddit(metadata.get("subreddit", "")),
        "author": metadata.get("author", ""),
        "score": _parse_int(metadata.get("score"), 0),
        "num_comments": _parse_int(metadata.get("num_comments"), 0),
    }, [str(comment).strip() for comment in comments if str(comment).strip()]


def _scrape_reddit_page(
    clean_url: str,
    limit: int,
    include_replies: bool,
) -> tuple[dict[str, Any], list[str]]:
    _require_playwright()

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        browser = None
        context = None
        page = None

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=USER_AGENT,
                    locale="en-US",
                    viewport=VIEWPORT,
                )
                page = context.new_page()
                page.set_default_timeout(ACTION_TIMEOUT_MS)

                response = page.goto(
                    clean_url,
                    wait_until="networkidle",
                    timeout=PAGE_LOAD_TIMEOUT_MS,
                )

                if response is not None and response.status >= 400:
                    raise RuntimeError(
                        f"Reddit returned HTTP {response.status} for the post URL."
                    )

                _dismiss_overlays(page)
                _wait_for_post(page)
                _scroll_comment_section(page, limit, include_replies)

                metadata, comments = _extract_page_data(page, include_replies)

                browser.close()
                return metadata, comments

        except (PlaywrightError, PlaywrightTimeoutError, RuntimeError) as exc:
            last_error = exc
            logger.warning(
                "Reddit scrape attempt %s/%s failed for %s: %s",
                attempt,
                MAX_RETRIES,
                clean_url,
                exc,
            )

            for resource in (page, context, browser):
                if resource is None:
                    continue
                try:
                    if hasattr(resource, "close"):
                        resource.close()
                except Exception:
                    pass

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    message = (
        "Failed to fetch Reddit discussion after "
        f"{MAX_RETRIES} attempts.\n\n{last_error}"
    )
    raise RuntimeError(message) from last_error


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_reddit_post_metadata(reddit_url: str) -> dict[str, Any]:
    clean_url = normalize_reddit_url(reddit_url)

    cached = _cache_get(clean_url)
    if cached is not None:
        return dict(cached.metadata)

    metadata, comments = _scrape_reddit_page(
        clean_url,
        limit=min(DEFAULT_LIMIT, MAX_LIMIT),
        include_replies=False,
    )
    _cache_set(
        clean_url,
        metadata,
        comments,
        limit=min(DEFAULT_LIMIT, MAX_LIMIT),
        include_replies=False,
    )
    return dict(metadata)


def fetch_reddit_comments(
    reddit_url,
    limit=200,
    include_replies=False,
):
    clean_url = normalize_reddit_url(reddit_url)
    limit = max(1, min(int(limit), MAX_LIMIT))

    cached = _cache_get(clean_url)
    if cached is not None and _cache_covers(cached, limit, include_replies):
        return _filter_comments(cached.comments, include_replies, limit)

    metadata, comments = _scrape_reddit_page(
        clean_url,
        limit=limit,
        include_replies=include_replies,
    )
    _cache_set(clean_url, metadata, comments, limit, include_replies)
    return _filter_comments(comments, include_replies, limit)
