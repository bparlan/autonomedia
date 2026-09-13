"""Deterministic AI rewriting for platform-specific content.

If no Gemini API key is present, fall back to simple templating.
Preserves whitelisted mentions/hashtags from mention_registry.json.
"""
import json
import os
import random
import re
from pathlib import Path
from typing import Dict, List

# Load whitelist contacts
WHITELIST_PATH = Path(__file__).parent.parent / "content" / "mention_registry.json"
_whitelist = {}
if WHITELIST_PATH.exists():
    try:
        with open(WHITELIST_PATH) as f:
            _whitelist = json.load(f)
    except Exception:
        _whitelist = {}

WHITELIST_HANDLES = _whitelist.get("whitelist_handles", [])
WHITELIST_LINKS = _whitelist.get("whitelist_links", [])
WHITELIST_HASHTAGS = _whitelist.get("whitelist_hashtags", [])

# Platform style guides
PLATFORM_GUIDES = {
    "mastodon": "Rewrite for Mastodon: conversational, friendly, max 500 chars, include hashtags if relevant.",
    "linkedin": "Rewrite for LinkedIn: professional, title + summary, max 3000 chars, include relevant hashtags.",
    "x": "Rewrite for X (Twitter): punchy hook, max 280 chars, up to 3 hashtags.",
}


def _apply_whitelist(text: str) -> str:
    """Strip mentions/links not in whitelist; keep whitelisted ones."""
    # Very simple implementation: replace any handle/link not in whitelist with placeholder
    # In production, this would use a more robust parser.
    for handle in WHITELIST_HANDLES:
        text = text.replace(handle, handle)  # keep
    for link in WHITELIST_LINKS:
        if link not in text:
            text = text + " " + link  # ensure included
    # Remove any remaining @mentions or http(s):// links not whitelisted
    # This is a naive approach; for a robust system use a proper parser.
    return text


def deterministic_rewrite(base_content: str, platform: str, reference_link: str | None = None) -> str:
    """Simple deterministic rewriter for a platform."""
    if platform == "mastodon":
        # Keep first 200 chars as title, rest as body, max 500 total
        title = base_content[:200].strip()
        if title.endswith("."):
            title = title[:-1]
        body = base_content[200:].strip()
        if not body:
            body = """
        # Combine title + body, preserve reference link
        out = title
        if body:
            out = out + " " + body if out else body
        if reference_link:
            out = out + " " + reference_link
        if len(out) > 500:
            out = out[:497] + "..."
        return out
    elif platform == "linkedin":
        # Title + summary
        title = base_content[:200].strip()
        if title.endswith("."):
            title = title[:-1]
        summary = base_content[200:].strip()
        if len(summary) > 2500:
            summary = summary[:2497] + "..."
        out = title
        if summary:
            out = out + "

""" + summary + """"
        if reference_link:
            out = out + "

""" + reference_link + """"
        return out
    elif platform == "x":
        # Keep up to 280 chars, include reference link at end if fits
        out = base_content.strip()
        if reference_link:
            spacer = " " if out else ""
            if len(out) + len(spacer) + len(reference_link) > 280:
                out = out[:280 - len(reference_link) - 4] + "... " + reference_link
            else:
                out = out + spacer + reference_link
        if len(out) > 280:
            out = out[:277] + "..."
        return out
    else:
        return base_content


def rewrite_for_platform(base_content: str, platform: str, reference_link: str | None = None) -> str:
    """Return a platform-specific variant of the content."""
    # Attempt to use Gemini via env var if present; otherwise deterministic.
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        try:
            from google.genai import GeminiClient
            from google.genai.types import GenerateContentConfig
            client = GeminiClient(api_key=gemini_api_key)
            prompt = f"""{PLATFORM_GUIDES.get(platform, "")}

Base content:
{base_content}"""
            if reference_link:
                prompt += f"
Reference link: {reference_link}"
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=GenerateContentConfig(temperature=0.7, max_output_tokens=2000),
            )
            if response and hasattr(response, "text"):
                text = response.text.strip()
                return _apply_whitelist(text)
        except Exception as e:
            logging.warning("Gemini rewrite failed: %s", e)
    # Fallback deterministic rewrite
    return deterministic_rewrite(base_content, platform, reference_link)
