"""X (Twitter) platform handler."""

import asyncio
import logging
import random
import re
from typing import Any

from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings
from autonomedia.core.platform.base import PlatformHandler

logger = logging.getLogger("x_handler")


class XHandler(PlatformHandler):
    """Handler for X (Twitter) posting."""

    CHARACTER_LIMIT = 280
    CHARACTER_LIMITS = {"tweet": 280, "thread": 1000, "reply": 1000}
    FIELD_LIMITS = {
        "hashtags": {"max_count": 3, "max_length": 25},
        "mentions": {"max_count": 1, "max_length": 50},
    }
    MAX_RETRIES = 3
    BASE_DELAY = 2.0  # seconds

    def __init__(self, browser_data_dir: str, task_id: str | None = None, auth_token: str | None = None):
        super().__init__(browser_data_dir, task_id)
        self.auth_token = auth_token or self._get_auth_token()
        self.x_url = settings.X_URL if hasattr(settings, "X_URL") else "https://x.com"

    def _get_random_ua_for_browser(self) -> str:
        """Selects a random user agent from BrowserProvider's list."""
        # Accessing USER_AGENTS directly from BrowserProvider class
        return random.choice(BrowserProvider.USER_AGENTS)
    def _get_auth_token(self) -> str | None:
        """Get authentication token from environment."""
        token = settings.X_AUTH_TOKEN
        if not token:
            logger.error("X_AUTH_TOKEN environment variable not set")
        return token

    def truncate_tweet(self, content: str, article_link: str | None = None) -> str:
        """Truncate content to 280 characters with ellipsis, preserving the article link."""
        if article_link:
            # Calculate available space for content, excluding link and ellipsis
            # Subtract 4 for ellipsis "..." and space " " before the link
            available_space = self.CHARACTER_LIMIT - len(article_link) - 4
        else:
            # If no link, allow full 280 characters minus ellipsis
            available_space = self.CHARACTER_LIMIT - 3  # 3 for "..."

        if len(content) > available_space:
            truncated_content = content[:available_space]
            return truncated_content.rstrip() + "..."
        else:
            return content

    def extract_hashtags(self, content: str) -> list[str]:
        """Extract hashtags from content.

        Rules:
        - Max 3 hashtags
        - Format: #Hashtag (camelCase)
        - No duplicates
        """
        # Extract hashtags
        hashtags = re.findall(r"#(\w+)", content)

        # Deduplicate and limit
        seen = set()
        formatted_hashtags = []

        for tag in hashtags[: self.FIELD_LIMITS["hashtags"]["max_count"]]:
            if tag in seen:
                continue
            seen.add(tag)

            # Format: #Hashtag (camelCase)
            formatted_tag = f"#{tag[0].upper()}{tag[1:]}"
            formatted_hashtags.append(formatted_tag)

        return formatted_hashtags

    def preserve_hook(self, content: str) -> str:
        """Preserve the first line as a strong hook."""
        lines = content.split("\n", 1)
        if len(lines) > 1:
            return lines[0] + " " + lines[1]
        return content

    def preserve_article_link(self, content: str, article_link: str | None = None) -> str:
        """Preserve article link at the end of the tweet."""
        if not article_link:
            return content

        # Ensure link is at the end
        link = f"\n\n{article_link}"
        return content.rstrip() + link

    def format_tweet(
        self, content: str, hashtags: list[str], article_link: str | None = None
    ) -> str:
        """Format X tweet with hook, hashtags, and article link, respecting character limits.

        Args:
            content: The main content of the tweet.
            hashtags: A list of hashtags to include.
            article_link: The URL of the article to append.

        Returns:
            The formatted tweet string, truncated if necessary.
        """
        # 1. Apply hook to content to ensure the first line is prominent.
        processed_content = self.preserve_hook(content)

        # 2. Append hashtags, ensuring a space before them.
        if hashtags:
            # Format hashtags as: #Tag1 #Tag2
            # The character limit will be checked after all components are added.
            processed_content += " " + " ".join(hashtags)

        # 3. Append article link if provided.
        # preserve_article_link adds necessary newlines and handles trailing content.
        if article_link:
            processed_content = self.preserve_article_link(processed_content, article_link)

        # 4. Truncate the entire combined string to fit the character limit.
        # truncate_tweet handles adding ellipsis and ensuring the final string is within the limit.
        formatted_tweet = self.truncate_tweet(processed_content)
        return formatted_tweet

    async def validate_auth(self) -> bool:
        """Validate X authentication."""
        if not self.auth_token:
            logger.error("No authentication token found for X")
            self.log_event("Auth validation failed: no token available", level="error")
            return False
        
        self.log_event("X authentication validated successfully", level="info")
        return True
    async def get_rate_limit_status(self) -> dict:
        """Get rate limit status for X (Twitter).

        X API has a 300 tweets per 3 hours limit.
        Returns configured limits when no active session available.
        """
        return {
            "platform": "x",
            "remaining": 300,
            "limit": 300,
            "window_seconds": 10800,
            "reset_time": None,
            "note": "X has 300 tweets per 3-hour window limit",
        }

    async def _check_session_health(self) -> bool:
        """Check if the X session is healthy. Validate token presence and freshness."""
        logger.info(f"Checking X session health for task {self.task_id or ''}...")
        
        # Check token presence
        if not self.auth_token:
            logger.error("No authentication token found for X. Cannot proceed with posting.")
            self.log_event("Session health check failed: no token available", level="error")
            return False
        
        # TODO: Implement robust session validation: check token expiry, potentially refresh
        # In a real implementation, you would check self.auth_token expiry and refresh if needed
        # Example: if token_expired(self.auth_token):
        #             await self._refresh_token()
        #             if not self.auth_token: return False # Refresh failed
        
        logger.info("X session health check passed")
        return True

    async def post(self, content: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Post content to X (Twitter) with retry logic for rate limits."""
        options = options or {}
        batch_mode = options.get("batch_mode", False) # Keeping these for signature compatibility, though not directly used in retry logic here
        max_delay = options.get("max_delay", 10.0)

        # Normalize content, extract hashtags, and format tweet
        content = await self.normalize_content(content)
        extracted_hashtags = self.extract_hashtags(content)
        options_hashtags = options.get("hashtags", [])
        hashtags = options_hashtags if options_hashtags else extracted_hashtags
        article_link = options.get("article_link")
        formatted_tweet = self.format_tweet(content, hashtags, article_link)

        self.log_event(f"Attempting to post to X: {formatted_tweet[:50]}...", self.task_id)

        MAX_RETRIES = 3
        BASE_DELAY = 2.0  # seconds for exponential backoff

        for attempt in range(MAX_RETRIES + 1): # Loop for retries (0 to MAX_RETRIES)
            try:
                async with BrowserProvider(self.browser_data_dir, task_id=self.task_id, user_agent=self._get_random_ua_for_browser()) as context:
                    page = context.pages[0] if context.pages else await context.new_page()

                    viewports = [
                        {"width": 1280, "height": 800}, {"width": 1366, "height": 768}, {"width": 1536, "height": 864},
                    ]
                    viewport = random.choice(viewports)
                    await page.set_viewport_size(viewport)

                    self.log_event("Navigating to X", self.task_id)
                    await context._human_delay()
                    await page.goto(self.x_url, wait_until='load')
                    await self.random_delay(0.5, 2.5)

                    # Re-locate compose_textarea in each attempt or ensure it's initialized correctly.
                    compose_textarea_locator_str = "div[contenteditable='true']"
                    compose_textarea = page.locator(compose_textarea_locator_str)

                    if await compose_textarea.count() == 0:
                        raise ValueError(f"X compose area not found with selector: {compose_textarea_locator_str}")

                    await compose_textarea.first.wait_for(state='visible')
                    compose_textarea.first.fill(formatted_tweet)
                    await self.random_delay(0.5, 2.5)

                    # Submit tweet
                    self.log_event("Submitting tweet", self.task_id)
                    post_button_locator_str = "button[data-testid='tweetButton']"
                    post_button = page.locator(post_button_locator_str)
                    await asyncio.sleep(random.uniform(1, 3))
                    await context._human_delay()
                    await post_button.wait_for(state='visible')

                    if await post_button.is_disabled():
                        raise ValueError("Post button is disabled")

                    await self.random_delay(0.5, 2.5)
                    await post_button.click()

                    # Verify tweet
                    self.log_event("Verifying tweet", self.task_id)
                    await self.random_delay(1, 2)
                    await page.wait_for_selector("div[aria-label='Tweet']", state="visible", timeout=15000)

                    self.log_event("Tweet successful", self.task_id)
                    return {
                        "status": "success",
                        "content": formatted_tweet,
                        "platform": "x",
                        "character_count": len(formatted_tweet),
                    }
            except Exception as e:
                # Check if it's a rate limit error (HTTP 429 or "rate limit" in message)
                is_rate_limit_error = False
                
                # Check HTTP status code in error message using regex
                status_match = re.search(r'Status\s*(\d{3})', str(e))
                if status_match and status_match.group(1) == '429':
                    is_rate_limit_error = True
                    self.log_event(f"Detected HTTP 429 rate limit error: {e}", self.task_id, level="warning")
                elif '429' in str(e):
                    # Fallback: check if status code 429 appears in the error message
                    is_rate_limit_error = True
                    self.log_event(f"Detected HTTP 429 error: {e}", self.task_id, level="warning")
                elif 'rate limit' in str(e).lower():
                    # Check if error message contains "rate limit"
                    is_rate_limit_error = True
                    self.log_event(f"Detected rate limit error: {e}", self.task_id, level="warning")
                elif hasattr(e, 'message') and isinstance(e.message, str):
                    # Check Playwright-specific error messages
                    if '429' in e.message or 'rate limit' in e.message.lower():
                        is_rate_limit_error = True
                        self.log_event(f"Detected Playwright rate limit error: {e}", self.task_id, level="warning")

                if is_rate_limit_error and attempt < MAX_RETRIES:
                    # Calculate exponential backoff delay: base_delay * 2^attempt
                    # Delay will be 2s, 4s, 8s for attempts 0, 1, 2 (which are retries 1, 2, 3)
                    delay = BASE_DELAY * (2 ** attempt) * random.uniform(0.8, 1.2) # Adding jitter
                    self.log_event(f"Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay:.2f} seconds. Error: {e}", self.task_id)
                    await asyncio.sleep(delay)
                else:
                    # Log the final error and return
                    self.log_event(f"X Post failed after {attempt + 1} attempts. Last error: {e}", self.task_id)
                    return {
                        "status": "error",
                        "message": str(e),
                        "platform": "x",
                        "attempts": attempt + 1,
                    }

        # Should not reach here if loop logic is correct and always returns
        self.log_event("Unexpected exit from X post logic.", self.task_id)
        return {
            "status": "error",
            "message": "Unexpected state reached in X post handler.",
            "platform": "x",
        }

    async def batch_post(
        self, contents: list[str], options: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Post multiple tweets with random delays between them."""
        options = options or {}
        results = []

        for i, content in enumerate(contents):
            self.log_event(f"Processing tweet {i + 1}/{len(contents)} for batch post", self.task_id)

            delay_range = (5, 10) # Use 5-10s for batch posts as per requirement

            if i > 0:
                await self.random_delay(*delay_range)

            # The post method now handles retries internally.
            try:
                result = await self.post(content, options)
                # Append both success and failed results from post()
                results.append(result)
            except Exception as e:
                # If a single post fails after retries, log it and continue with the next.
                # This prevents one failed tweet from stopping the entire batch.
                self.log_event(f"Failed to post tweet {i+1}: {e}")
                results.append({
                    "status": "failed",
                    "content": content,
                    "platform": "x",
                    "error": str(e),
                    "character_count": len(content) # Approximate, could be truncated
                })
            
            # Add a small delay between processing each item in the batch, regardless of retries.
            await asyncio.sleep(random.uniform(0.5, 1.5))

        # Delay after the entire batch is processed.
        await asyncio.sleep(random.uniform(*delay_range))
        return results
