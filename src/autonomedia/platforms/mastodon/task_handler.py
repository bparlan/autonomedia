"""Mastodon platform handler."""

import logging
import random
import re
from typing import Any

from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings
from autonomedia.core.platform.base import PlatformHandler

logger = logging.getLogger("mastodon_adapter")


class MastodonHandler(PlatformHandler):
    """Handler for Mastodon posting."""

    CHARACTER_LIMITS = {"toot": 500, "status": 500, "note": 500}
    FIELD_LIMITS = {
        "tags": {"max_count": 5, "max_length": 25},
        "emojis": {"max_count": 4, "max_length": 20},
    }

    def __init__(self, browser_data_dir: str, task_id: str | None = None, auth_token: str | None = None):
        super().__init__(browser_data_dir, task_id)
        self.auth_token = auth_token or self._get_auth_token()
        self.mastodon_url = settings.MASTODON_URL if hasattr(settings, "MASTODON_URL") else "https://mastodon.social"

    def _get_auth_token(self) -> str | None:
        """Get authentication token from environment."""
        token = settings.MASTODON_AUTH_TOKEN
        if not token:
            logger.error("MASTODON_AUTH_TOKEN environment variable not set")
        return token

    def extract_title(self, content: str) -> str:
        """Extract title from content.

        First 200 chars max, but will not exceed 300 characters (Mastodon limit for titles).
        """
        content = self.normalize_content(content)
        title = content[:200].strip()
        
        # Remove trailing period if present (professional tone requirement)
        if title.endswith("."):
            title = title[:-1]
        
        # Truncate if exceeded max_length
        if len(title) > 300:
            title = title[:300].strip()
            if title.endswith("."):
                title = title[:-1]
        
        return title

    def extract_summary(self, content: str, title: str) -> str:
        """Extract summary from remaining content.

        Max 3000 characters (Mastodon limit for status updates).
        """
        content = self.normalize_content(content)
        
        # Remove the title from the beginning
        if content.startswith(title):
            content = content[len(title):].lstrip()
        
        # Remove excessive whitespace
        content = re.sub(r"\s+", " ", content).strip()
        
        # Truncate if exceeded max_length
        if len(content) > 3000:
            content = content[:3000].strip()
        
        # Remove trailing period if present (professional tone requirement)
        if content.endswith("."):
            content = content[:-1]
        
        return content

    def extract_hashtags(self, content: str) -> list:
        """Extract hashtags from content.

        Rules:
        - Max 5 hashtags
        - Format: #Hashtag (camelCase)
        - No duplicates
        """
        # Extract hashtags
        hashtags = re.findall(r"#(\w+)", content)
        
        # Deduplicate and limit
        seen = set()
        formatted_hashtags = []
        
        for tag in hashtags[: self.FIELD_LIMITS["tags"]["max_count"]]:
            if tag in seen:
                continue
            seen.add(tag)
            
            # Format: #Hashtag (camelCase)
            formatted_tag = f"#{tag[0].upper()}{tag[1:]}"
            formatted_hashtags.append(formatted_tag)
        
        return formatted_hashtags

    def extract_article_link(self, content: str) -> str:
        """Extract and preserve article link at the end."""
        # Look for common URL patterns (http/https)
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, content)
        
        if urls:
            # Return the last URL found
            return urls[-1]
        return ""

    def format_post(
        self, content: str, hashtags: list, article_link: str | None = None
    ) -> str:
        """Format Mastodon toot with title, summary, hashtags, and article link.

        Rules:
        - Title: First 200 chars (max 300), no trailing period
        - Summary: Remaining content (max 3000), no trailing period
        - Hashtags: Max 5, camelCase, no duplicates
        - Article link: Included at the end
        """
        # Extract title and summary
        title = self.extract_title(content)
        summary = self.extract_summary(content, title)
        
        # Extract hashtags from content
        extracted_hashtags = self.extract_hashtags(content)
        options_hashtags = hashtags if hashtags else extracted_hashtags
        
        # Format hashtags
        formatted_hashtags = []
        seen = set()
        for tag in options_hashtags[: self.FIELD_LIMITS["tags"]["max_count"]]:
            if tag in seen:
                continue
            seen.add(tag)
            formatted_hashtags.append(tag)
        
        # Build post parts (no delays here - they're in post method)
        post_parts = []
        
        # Add title (without trailing period)
        if title:
            post_parts.append(title)
        
        # Add summary (without trailing period)
        if summary:
            post_parts.append(summary)
        
        # Add hashtags
        if formatted_hashtags:
            post_parts.append(" ".join(formatted_hashtags))
        
        # Add article link at the end
        if article_link:
            post_parts.append(article_link)
        
        # Combine all parts
        final_content = " ".join(post_parts)
        
        return final_content

    async def validate_auth(self) -> bool:
        """Validate Mastodon authentication."""
        if not self.auth_token:
            logger.error("No authentication token found for Mastodon")
            self.log_event("Auth validation failed: no token available", level="error")
            return False
        
        self.log_event("Mastodon authentication validated successfully", level="info")
        return True
    async def get_rate_limit_status(self) -> dict:
        """Get rate limit status for Mastodon.

        Mastodon instances typically don't have strict rate limits, but we return
        None values to indicate this. Operators should use polite posting intervals.
        """
        return {
            "platform": "mastodon",
            "remaining": None,
            "limit": None,
            "reset_time": None,
            "note": "Mastodon has no strict rate limits; use polite posting intervals (1-2s between posts)",
        }

    async def _check_session_health(self) -> bool:
        """Check if the Mastodon session is healthy. Validate token presence and freshness."""
        logger.info(f"Checking Mastodon session health for task {self.task_id or ''}...")
        
        # Check token presence
        if not self.auth_token:
            logger.error("No authentication token found for Mastodon. Cannot proceed with posting.")
            self.log_event("Session health check failed: no token available", level="error")
            return False
        
        # TODO: Implement robust session validation: check token expiry, potentially refresh
        # In a real implementation, you would check self.auth_token expiry and refresh if needed
        # Example: if token_expired(self.auth_token):
        #             await self._refresh_token()
        #             if not self.auth_token: return False # Refresh failed
        
        logger.info("Mastodon session health check passed")
        return True

    async def post(self, content: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Post content to Mastodon.

        Args:
            content: Raw content to post
            options: {
                "hashtags": Optional[list],
                "article_link": Optional[str],
            }

        Returns:
            Dict with status and metadata
        """
        options = options or {}
        
        # Normalize content
        content = await self.normalize_content(content)
        
        # Extract hashtags from content
        extracted_hashtags = self.extract_hashtags(content)
        options_hashtags = options.get("hashtags", [])
        hashtags = options_hashtags if options_hashtags else extracted_hashtags
        
        # Get article link
        article_link = options.get("article_link")
        
        # Format the toot
        formatted_post = self.format_post(content, hashtags, article_link)
        
        self.log_event(f"Posting to Mastodon: {formatted_post[:50]}...")
        
        try:
            async with BrowserProvider(self.browser_data_dir, task_id=self.task_id) as context:
                page = context.pages[0] if context.pages else await context.new_page()

                # Randomized viewport for anti-detection
                viewports = [
                    {"width": 1280, "height": 800},
                    {"width": 1366, "height": 768},
                    {"width": 1536, "height": 864},
                ]
                viewport = random.choice(viewports)
                await page.set_viewport_size(viewport)

                self.log_event("Navigating to Mastodon", self.task_id)
                await page.goto(self.mastodon_url)
                await self.random_delay(0.5, 2.5)

                # Session health check
                login_indicators = await page.get_by_role(
                    "link", name=re.compile(r"Log in|Sign in|Join", re.IGNORECASE)
                ).count()
                
                if login_indicators > 0:
                    self.log_event("Auth expired", self.task_id, level="error")
                    raise ValueError(
                        "Session Health Check Failed: Auth expired. User must re-authenticate the profile."
                    )

                self.log_event("Session health verified", self.task_id)

                # Compose toot
                self.log_event("Composing toot", self.task_id)
                compose_textarea = page.get_by_placeholder("What's on your mind?")
                
                if not await compose_textarea.count():
                    compose_textarea = page.locator(
                        ".compose-form__autosuggest-wrapper textarea, "
                        ".compose-form__autosuggest-wrapper div[contenteditable='true']"
                    )
                
                if await compose_textarea.count() == 0:
                    self.log_event("Compose area not found", self.task_id, level="error")
                    raise ValueError(
                        "Compose area not found (session might be expired or UI changed)"
                    )

                await compose_textarea.first.fill(formatted_post)
                await self.random_delay(0.5, 2.5)

                # Submit toot
                self.log_event("Submitting toot", self.task_id)
                post_button = page.get_by_role(
                    "button", name=re.compile(r"^(Post|Publish)$", re.IGNORECASE)
                )
                await post_button.wait_for(state="visible")

                if await post_button.is_disabled():
                    self.log_event("Post button disabled", self.task_id, level="error")
                    raise ValueError(
                        "Post button is disabled (Content may violate platform rules or limits not caught by adapter)"
                    )

                await self.random_delay(0.5, 2.5)
                await post_button.click()

                # Verify toot
                self.log_event("Verifying toot", self.task_id)
                await self.random_delay(1, 2)
                post_locator = page.get_by_text(formatted_post, exact=True)
                await post_locator.wait_for(state="visible", timeout=15000)

                self.log_event("Toot successful", self.task_id)
                return {
                    "status": "success",
                    "content": formatted_post,
                    "platform": "mastodon",
                    "character_count": len(formatted_post),
                }

        except Exception as e:
            self.log_event(f"Mastodon post failed: {str(e)}", self.task_id, level="error")
            raise
