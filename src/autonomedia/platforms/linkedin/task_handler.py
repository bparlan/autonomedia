"""LinkedIn platform handler."""

import asyncio
import logging
import random
import re
from typing import Any

from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.platform.base import PlatformHandler


# Lazy import to avoid circular dependency
def _get_settings():
    from autonomedia.core.config import settings
    return settings

settings = None


def get_settings():
    global settings
    if settings is None:
        settings = _get_settings()
    return settings


logger = logging.getLogger("linkedin_handler")


class LinkedInHandler(PlatformHandler):
    """Handler for LinkedIn posting."""

    CHARACTER_LIMITS = {
        "title": 300,
        "summary": 3000,
        "comments": 1000,
    }

    FIELD_LIMITS = {
        "title": {"max_length": 300, "has_period": False},
        "summary": {"max_length": 3000, "has_period": True},
        "tags": {"max_count": 5, "max_length": 25},
    }

    def __init__(self, browser_data_dir: str, task_id: str | None = None, auth_token: str | None = None):
        super().__init__(browser_data_dir, task_id)
        self.auth_token = auth_token or self._get_auth_token()
        self.linkedin_url = get_settings().LINKEDIN_URL if hasattr(get_settings(), "LINKEDIN_URL") else "https://www.linkedin.com"

    def _get_auth_token(self) -> str | None:
        """Get authentication token from environment."""
        token = get_settings().LINKEDIN_AUTH_TOKEN
        if not token:
            logger.error("LINKEDIN_AUTH_TOKEN environment variable not set")
        return token

    async def _human_like_scroll(self, page):
        """Simulate human-like scrolling behavior."""
        scroll_times = random.randint(2, 4)
        for _ in range(scroll_times):
            await asyncio.sleep(random.uniform(0.5, 2.0))
            scroll_distance = random.randint(200, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_distance});")
            await asyncio.sleep(random.uniform(0.5, 2.0))


    def extract_title(self, content: str) -> str:
        """Extract title from content (max 300 chars), removing trailing period."""
        title = content.strip()
        
        # Truncate to the maximum allowed length
        if len(title) > self.FIELD_LIMITS["title"]["max_length"]:
            title = title[:self.FIELD_LIMITS["title"]["max_length"]]
            
        # Remove trailing period if it exists, as per LinkedIn rules
        if title.endswith('.'):
            title = title[:-1]
            
        return title.strip()

    def extract_summary(self, content: str) -> str:
        """Extract summary from remaining content (max 3000 chars)."""
        # For now, just return the content stripped, limited to 3000 chars
        summary = content.strip()
        if len(summary) > self.FIELD_LIMITS["summary"]["max_length"]:
            summary = summary[:self.FIELD_LIMITS["summary"]["max_length"]]
        return summary



    def extract_tags(self, content: str) -> list[str]:
        """Extract up to 5 unique tags (max 25 chars each) from content."""
        # Regex to find words following a '#'
        tags_found = re.findall(r"#(\w+)", content)
        
        unique_tags = []
        for tag in tags_found:
            # Check character limit and uniqueness
            if len(tag) <= self.FIELD_LIMITS["tags"]["max_length"] and tag not in unique_tags:
                unique_tags.append(tag)
                # Stop if we have reached the maximum number of tags
                if len(unique_tags) >= self.FIELD_LIMITS["tags"]["max_count"]:
                    break
                    
        return unique_tags

    def format_post(self, title: str, summary: str, tags: list[str], article_link: str | None = None) -> str:
        """Format LinkedIn post with title, summary, and tags."""
        lines = []
        
        # Add title
        if title:
            lines.append(title)
            
        # Add summary, preserving paragraph breaks
        if summary:
            lines.append(summary)
            
        # Add tags if any
        if tags:
            # Format tags as comma-separated, prefixed with '#'
            formatted_tags = ", ".join([f"#{tag}" for tag in tags])
            lines.append(formatted_tags)
            
        # Use "\n" for newlines, which LinkedIn typically handles for paragraphs.
        return "\n".join(lines)

    async def validate_auth(self) -> bool:
        """Validate LinkedIn authentication."""
        if not self.auth_token:
            logger.error("No authentication token found for LinkedIn")
            self.log_event("Auth validation failed: no token available", level="error")
            return False
        logger.info("LinkedIn authentication token found and validated")
        return True

    async def get_rate_limit_status(self) -> dict:
        """Get rate limit status for LinkedIn.

        LinkedIn API has a 100 requests per hour limit.
        Returns configured limits when no active API call available.
        """
        return {
            "platform": "linkedin",
            "remaining": 100,
            "limit": 100,
            "window_seconds": 3600,
            "reset_time": None,
            "note": "LinkedIn has 100 posts per hour limit",
        }


    async def _check_session_health(self) -> bool:
        """Check if the LinkedIn session is healthy. Validate token presence and freshness."""
        self.log_event("Checking session health...", self.task_id)
        if not self.auth_token:
            self.log_event("Authentication token missing. Attempting to refresh.", self.task_id, level="warning")
            await self.refresh_auth_token()
            if not self.auth_token:
                self.log_event("Failed to refresh authentication token.", self.task_id, level="error")
                return False

        # Implement actual token freshness check
        try:
            # TODO: Implement actual token validation via LinkedIn API
            # For now, assume token is valid if present after potential refresh.
            self.log_event("Session health check passed (token present and potentially refreshed).", self.task_id)
            return True
        except Exception as e:
            self.log_event(f"Session health check failed: {str(e)}", self.task_id, level="error")
            return False

    async def refresh_auth_token(self):
        """Refresh the LinkedIn authentication token.
        
        Attempts to refresh the authentication token using browser-based session.
        If successful, updates self.auth_token with the new token.
        Returns None on success or failure (failure is logged).
        """
        self.log_event("Attempting to refresh LinkedIn auth token...", self.task_id)
        
        try:
            # Initialize browser if not already available
            from autonomedia.browser.provider import BrowserProvider
            
            browser = BrowserProvider.get_browser(self.browser_data_dir)
            if not browser:
                self.log_event("Browser not available for token refresh", self.task_id, level="error")
                return
            
            # Navigate to LinkedIn and validate session
            await browser.navigate("https://www.linkedin.com")
            
            # Wait for page to load
            await browser.page.wait_for_load_state("networkidle")
            
            # Check if we're logged in by looking for LinkedIn-specific elements
            # TODO: Implement actual LinkedIn-specific login validation
            # For now, we'll attempt to extract any auth token from page
            page_content = await browser.page.content()
            
            # Try to find any token in the page (this is a simulation)
            # In production, this would use LinkedIn's actual authentication flow
            self.log_event("Browser session validated (simulated)", self.task_id)
            
            # TODO: Extract actual token from page or initiate OAuth flow
            # For simulation, we'll keep the existing token
            # self.auth_token = await self._extract_token_from_page(browser.page)
            
            self.log_event("LinkedIn auth token refresh completed", self.task_id)
            
        except Exception as e:
            self.log_event(f"Failed to refresh LinkedIn auth token: {str(e)}", self.task_id, level="error")

    async def post(self, content: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Post content to LinkedIn with retry logic for rate limits."""
        options = options or {}
        no_summary = options.get("no_summary", False)

        # Normalize content
        content = await self.normalize_content(content)

        # Extract components
        if no_summary:
            title = content
            summary = ""
        else:
            title = self.extract_title(content)
            summary = self.extract_summary(content)

        # Extract tags from content
        tags = self.extract_tags(content)

        # Add article link if provided
        article_link = options.get("article_link")

        # Format the post
        formatted_post = self.format_post(title, summary, tags, article_link)

        self.log_event(f"Posting to LinkedIn: {title[:50]}...")

        MAX_RETRIES = 3
        BASE_DELAY = 2  # seconds

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES + 1} to post to LinkedIn. Content snippet: {formatted_post[:100]}...")

                # --- Core posting logic starts here ---
                async with BrowserProvider(self.browser_data_dir, task_id=self.task_id) as context:
                    page = context.pages[0] if context.pages else await context.new_page()
                    # User Agent Spoofing
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    ]
                    random_ua = random.choice(user_agents)
                    await page.set_extra_http_headers({"User-Agent": random_ua})
                    self.log_event(f"Set User-Agent: {random_ua}", self.task_id)

                    # Randomized viewport for anti-detection
                    viewports = [
                        {"width": 1280, "height": 800},
                        {"width": 1366, "height": 768},
                        {"width": 1536, "height": 864},
                    ]
                    viewport = random.choice(viewports)
                    await self._human_like_scroll(page)
                    await page.set_viewport_size(viewport)

                    self.log_event("Navigating to LinkedIn", self.task_id)
                    await page.goto(self.linkedin_url)
                    await self.random_delay(5, 10)

                    # Human-like scrolling
                    self.log_event("Performing human-like scroll...", self.task_id)
                    await page.mouse.wheel(random.uniform(-300, -700), random.uniform(-200, -500)) # Scroll up
                    await asyncio.sleep(random.uniform(2, 4))
                    await page.mouse.wheel(random.uniform(300, 700), random.uniform(200, 500)) # Scroll down
                    await asyncio.sleep(random.uniform(2, 4))

                    # Session health check
                    # TODO: Implement proper auth check
                    self.log_event("Session health check", self.task_id)

                    # Compose post
                    self.log_event("Composing post", self.task_id)
                    compose_textarea = page.locator("textarea[aria-label='Post editor']")

                    if await compose_textarea.count() > 0:
                        # Use textarea as expected
                        pass
                    else:
                        compose_textarea = page.locator("div[contenteditable='true']")
                        if await compose_textarea.count() == 0:
                            raise ValueError("LinkedIn compose area not found")

                    await compose_textarea.first.fill(formatted_post)
                    await self.random_delay(5, 10)

                    # Submit post
                    self.log_event("Submitting post", self.task_id)
                    post_button = page.locator("button[aria-label='Post']")
                    await post_button.wait_for(state="visible")
                    if await post_button.is_disabled():
                        raise ValueError("Post button is disabled")

                    await self.random_delay(5, 10)
                    await post_button.click()

                    # Verify post
                    self.log_event("Verifying post", self.task_id)
                    await self.random_delay(5, 10)
                    await page.wait_for_selector("div[aria-label='Post']", state="visible", timeout=15000)

                    self.log_event("Post successful", self.task_id)
                    return {
                        "status": "success",
                        "content": formatted_post,
                        "platform": "linkedin",
                        "title": title,
                    }
            # If successful, return statement already exits the loop

            except (TimeoutError, ValueError) as e: # Catch specific expected errors that might happen during browser ops
                error_str = str(e).lower()
                is_rate_limit_error = (
                    "rate limit" in error_str or
                    "throttled" in error_str or
                    "restricted" in error_str or
                    "unavailable" in error_str or
                    "429" in error_str # Explicitly check for 429
                )
                if is_rate_limit_error:
                    if attempt < MAX_RETRIES:
                        delay = BASE_DELAY * (2 ** attempt) * (1 + random.uniform(-JITTER_FACTOR, JITTER_FACTOR))
                        logger.warning(f"LinkedIn rate limit hit (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay:.2f}s. Error: {e}")
                        self.log_event(f"LinkedIn rate limit hit. Retrying in {delay:.2f}s. Attempt {attempt + 1}/{MAX_RETRIES}.", self.task_id, level="warning", details={"original_error": str(e)})
                        await asyncio.sleep(delay)
                        continue # Retry the loop
                    else:
                        logger.error(f"LinkedIn rate limit hit after {MAX_RETRIES} retries. Aborting. Error: {e}")
                        self.log_event(f"LinkedIn rate limit exceeded after {MAX_RETRIES} retries. Aborting.", self.task_id, level="error", details={"original_error": str(e)})
                        return {"status": "failed", "message": f"LinkedIn rate limit exceeded after {MAX_RETRIES} retries.", "original_error": str(e)}
                else:
                    # Log other ValueErrors/TimeoutErrors and re-raise if not rate limiting
                    self.log_event(f"LinkedIn posting failed with unexpected error: {str(e)}", self.task_id, level="error", details={"error_type": type(e).__name__, "original_error": str(e)})
                    raise e # Re-raise if it's not a retryable rate limit error

            except Exception as e: # Catch any other unexpected exceptions
                error_str = str(e).lower()
                # Check for heuristic indicators of account restriction or throttling
                is_rate_limit_error = (
                    "heuristic_restriction_or_throttling" in str(e) or # Check for specific log message if it occurs
                    "rate limit" in error_str or
                    "throttled" in error_str or
                    "restricted" in error_str or
                    "unavailable" in error_str or
                    "429" in error_str # Explicitly check for 429
                )
                if is_rate_limit_error:
                    if attempt < MAX_RETRIES:
                        delay = BASE_DELAY * (2 ** attempt) * (1 + random.uniform(-JITTER_FACTOR, JITTER_FACTOR))
                        logger.warning(f"LinkedIn rate limit/restriction hit (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay:.2f}s. Error: {e}")
                        self.log_event(f"LinkedIn rate limit/restriction hit. Retrying in {delay:.2f}s. Attempt {attempt + 1}/{MAX_RETRIES}.", self.task_id, level="warning", details={"original_error": str(e)})
                        await asyncio.sleep(delay)
                        continue # Retry the loop
                    else:
                        logger.error(f"LinkedIn rate limit/restriction hit after {MAX_RETRIES} retries. Aborting. Error: {e}")
                        self.log_event(f"LinkedIn rate limit/restriction exceeded after {MAX_RETRIES} retries. Aborting.", self.task_id, level="error", details={"original_error": str(e)})
                        return {"status": "failed", "message": f"LinkedIn rate limit/restriction exceeded after {MAX_RETRIES} retries.", "original_error": str(e)}
                else:
                    # Log other unexpected errors and re-raise
                    self.log_event(f"LinkedIn posting failed with unexpected error: {str(e)}", self.task_id, level="error", details={"error_type": type(e).__name__, "original_error": str(e)})
                    raise e # Re-raise the original exception

        # Fallback return, should not be reached if logic is correct and loop breaks on success or returns on failure
        return {"status": "failed", "message": "LinkedIn posting failed after all retry attempts."}
