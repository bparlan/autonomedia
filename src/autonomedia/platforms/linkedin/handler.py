import asyncio
import json
import logging
import os
import random
import re
from datetime import UTC, datetime

from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings

# Configuration
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://www.linkedin.com")
LINKEDIN_BROWSER_DATA_DIR = os.path.join(settings.BASE_BROWSER_DATA_DIR, "linkedin")

# Character limits
TITLE_MAX_LENGTH = 300
TITLE_PREVIEW_LENGTH = 200
SUMMARY_MAX_LENGTH = 3000
TAGS_MAX_COUNT = 5
TAG_MAX_LENGTH = 25

# Anti-detection settings
MIN_DELAY = 0.5
MAX_DELAY = 2.5

logger = logging.getLogger("linkedin_handler")


def log_event(message, task_id, level="info", **kwargs):
    """Structured logging for LinkedIn handler."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": level,
        "message": message,
        "task_id": task_id,
        "platform": "linkedin",
        **kwargs,
    }
    logger.info(json.dumps(entry))


def normalize_text(text: str) -> str:
    """Strip markdown formatting and clean up text."""
    # Remove markdown formatting
    text = re.sub(r"[#*_`~\[\]]", "", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_title(text: str, max_length: int = TITLE_PREVIEW_LENGTH) -> str:
    """
    Extract title from content.
    First 200 chars max, but will not exceed TITLE_MAX_LENGTH (300).
    """
    text = normalize_text(text)
    preview = text[:max_length]
    
    # Remove trailing period if present (professional tone requirement)
    if preview.endswith("."):
        preview = preview[:-1]
    
    # Truncate if exceeded max_length
    if len(preview) > TITLE_MAX_LENGTH:
        preview = preview[:TITLE_MAX_LENGTH]
        if preview.endswith("."):
            preview = preview[:-1]
    
    return preview


def extract_summary(text: str, title: str) -> str:
    """
    Extract summary from remaining content.
    Max 3000 characters.
    """
    text = normalize_text(text)
    
    # Remove the title from the beginning
    if text.startswith(title):
        text = text[len(title):].lstrip()
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    # Truncate if exceeded max_length
    if len(text) > SUMMARY_MAX_LENGTH:
        text = text[:SUMMARY_MAX_LENGTH]
    
    # Remove trailing period if present (professional tone requirement)
    if text.endswith("."):
        text = text[:-1]
    
    return text


def extract_article_link(text: str) -> str:
    """Extract and preserve article link at the end."""
    # Look for common URL patterns (http/https)
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)

    if urls:
        # Return the last URL found
        return urls[-1]
    return ""


def extract_tags(text: str) -> list[str]:
    """Extract hashtags from text."""
    tag_pattern = r"#([a-zA-Z0-9_]+)"
    tags = re.findall(tag_pattern, text)
    return list(set(tags))  # Remove duplicates


def format_tag(tag: str) -> str:
    """Format tag to lowercase with underscores to spaces."""
    if not tag:
        return ""
    words = tag.lower().split("_")
    return "".join(word.capitalize() for word in words)


async def _human_delay():
    """Randomized delay to simulate human timing."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    log_event(
        f"Waiting {delay:.2f}s between actions to simulate human behavior",
        level="debug"
    )
    await asyncio.sleep(delay)


async def post_linkedin(content: str, options: dict, task_id: str = None):
    """
    Handle LinkedIn posting task with all required features.
    
    Args:
        content: The content to post
        options: Dict with platform-specific options
            - article_link: Optional article link to include
            - hashtags: Optional list of hashtags
        task_id: Optional task identifier for logging
    
    Returns:
        Dict with status and result
    """
    try:
        log_event("Starting LinkedIn post creation", task_id)

        # Extract options
        article_link = options.get("article_link", "")
        raw_hashtags = options.get("hashtags", [])

        # Extract and preserve strong hook (first line)
        hook = extract_first_line(content)

        # Extract article link from content if not provided
        if not article_link:
            article_link = extract_article_link(content)

        # Extract tags
        hashtags = extract_tags(content)
        formatted_tags = format_linkedin_tags(hashtags + raw_hashtags)

        # Create professional post format
        # Combine title (first 200 chars), summary, tags, and article link
        title = extract_title(content)
        summary = extract_summary(content, title)

        post_content_parts = []

        # Add title (without trailing period)
        if title:
            post_content_parts.append(title)
            await _human_delay()

        # Add summary (without trailing period)
        if summary:
            post_content_parts.append(summary)
            await _human_delay()

        # Add hashtags
        if formatted_tags:
            post_content_parts.append(formatted_tags)
            await _human_delay()

        # Add article link at the end
        if article_link:
            post_content_parts.append(article_link)

        # Combine all parts
        final_content = " ".join(post_content_parts)

        log_event(
            "Content prepared",
            task_id,
            length=len(final_content),
            title_length=len(title),
            summary_length=len(summary),
            tags_count=len(formatted_tags.replace("#", "").split()),
            article_link=article_link
        )

        # Create browser session
        async with BrowserProvider(LINKEDIN_BROWSER_DATA_DIR, task_id=task_id) as context:
            page = context.pages[0] if context.pages else await context.new_page()

            # Navigate to LinkedIn
            log_event("Navigating to LinkedIn", task_id)
            await page.goto(LINKEDIN_URL, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))  # Human-like delay

            # Session health check
            login_indicators = await page.get_by_role(
                "link", name=re.compile(r"Log in|Sign in|Join", re.IGNORECASE)
            ).count()
            if login_indicators > 0:
                log_event("Auth expired", task_id, level="error")
                raise Exception("Session Health Check Failed: Auth expired. User must re-authenticate.")

            log_event("Session health verified", task_id)

            # Find compose area (LinkedIn has multiple selectors)
            compose_textarea = page.get_by_role("textbox", name=re.compile(r"Post an update|Share|Write", re.IGNORECASE))

            if not await compose_textarea.count():
                compose_textarea = page.locator(
                    "div[contenteditable='true']", has_text=re.compile(r"Post|Share", re.IGNORECASE)
                )

            if await compose_textarea.count() == 0:
                log_event("Compose area not found", task_id, level="error")
                raise Exception("Compose area not found (session might be expired or UI changed)")

            log_event("Compose area found", task_id)

            # Type the post
            await compose_textarea.first.fill(final_content)
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

            # Find and click post button
            post_btn = page.get_by_role(
                "button", name=re.compile(r"^(Post|Share|Publish|Post now)$", re.IGNORECASE)
            )
            await post_btn.wait_for(state="visible", timeout=10000)

            if await post_btn.is_disabled():
                log_event("Post button disabled", task_id, level="error")
                raise Exception("Post button is disabled (content may violate platform rules)")

            log_event("Submitting post", task_id)
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            await post_btn.click()

            # Verify post
            log_event("Verifying post", task_id)
            await asyncio.sleep(random.uniform(1.0, 3.0))  # Wait for post to appear

            # LinkedIn uses text search but with partial matching
            post_locator = page.get_by_text(
                re.compile(re.escape(final_content[:50])),  # Partial text match
                exact=False
            )
            await post_locator.wait_for(state="visible", timeout=15000)

            log_event("Post successful", task_id, length=len(final_content))
            return {"status": "success", "content": final_content, "length": len(final_content)}

    except Exception as e:
        log_event(f"Task execution failed: {str(e)}", task_id, level="error")
        raise e


def format_linkedin_tags(hashtags: list[str]) -> str:
    """
    Format LinkedIn tags with camelCase naming, max 5 tags, max 25 chars each.
    """
    if not hashtags:
        return ""

    # Format each tag to camelCase
    formatted_tags = [format_tag(tag) for tag in hashtags]

    # Remove duplicates
    formatted_tags = list(dict.fromkeys(formatted_tags))  # Preserve order

    # Limit to max 5
    formatted_tags = formatted_tags[:TAGS_MAX_COUNT]

    # Filter tags that exceed max length
    formatted_tags = [
        tag[:TAG_MAX_LENGTH] for tag in formatted_tags 
        if len(tag) <= TAG_MAX_LENGTH
    ]

    return " ".join(f"#{tag}" for tag in formatted_tags)
def extract_first_line(text: str) -> str:
    """Extract the first line as strong hook."""
    lines = text.split("\n", 1)
    return lines[0].strip() if lines else text


async def batch_post_linkedin(contents: list[dict], task_id: str = None):
    """
    Post multiple content items to LinkedIn with randomized delays between posts.
    
    Args:
        contents: List of dicts with 'content' and optional 'options'
        task_id: Optional task identifier for logging
    
    Returns:
        List of results for each post
    """
    results = []

    log_event(f"Starting batch post with {len(contents)} items", task_id)

    for idx, content_item in enumerate(contents, 1):
        content = content_item.get("content", "")
        options = content_item.get("options", {})

        log_event(
            f"Processing batch item {idx}/{len(contents)}",
            task_id,
            item_idx=idx
        )

        try:
            result = await post_linkedin(content, options, task_id)
            results.append({
                "status": "success",
                "content": content,
                "result": result
            })
        except Exception as e:
            log_event(
                f"Batch item {idx} failed: {str(e)}",
                task_id,
                level="error",
                item_idx=idx
            )
            results.append({
                "status": "failed",
                "content": content,
                "error": str(e),
                "item_idx": idx
            })


async def batch_post_linkedin(contents: list[dict], task_id: str = None):
    """
    Post multiple content items to LinkedIn with randomized delays between posts.
    
    Args:
        contents: List of dicts with 'content' and optional 'options'
        task_id: Optional task identifier for logging
    
    Returns:
        List of results for each post
    """
    results = []

    log_event(f"Starting batch post with {len(contents)} items", task_id)

    for idx, content_item in enumerate(contents, 1):
        content = content_item.get("content", "")
        options = content_item.get("options", {})

        log_event(
            f"Processing batch item {idx}/{len(contents)}",
            task_id,
            item_idx=idx
        )

        try:
            result = await post_linkedin(content, options, task_id)
            results.append({
                "status": "success",
                "content": content,
                "result": result
            })
        except Exception as e:
            log_event(
                f"Batch item {idx} failed: {str(e)}",
                task_id,
                level="error",
                item_idx=idx
            )
            results.append({
                "status": "failed",
                "content": content,
                "error": str(e),
                "item_idx": idx
            })

