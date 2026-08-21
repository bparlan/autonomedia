"""Abstract base class for platform handlers."""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any

from autonomedia.browser.provider import BrowserProvider

logger = logging.getLogger("platform_base")


class PlatformHandler(ABC):
    """Abstract base class for platform-specific handlers.

    Provides common functionality:
    - BrowserProvider integration with anti-detection
    - Structured logging with timestamps
    - Retry logic with exponential backoff
    - Human-like delays for anti-detection
    - Content normalization
    """

    # Platform-specific constants (default values, can be overridden)
    CHARACTER_LIMITS: dict[str, int] = {
        "max_length": 280,
        "title_length": 200,
        "summary_length": 3000,
    }
    
    FIELD_LIMITS: dict[str, dict[str, int]] = {
        "tags": {
            "max_count": 5,
            "max_length": 25,
        },
        "description": {
            "max_length": 3000,
        },
    }

    def __init__(self, browser_data_dir: str, task_id: str | None = None):
        """Initialize platform handler.

        Args:
            browser_data_dir: Directory for browser profile data
            task_id: Optional task identifier for logging
        """
        self.browser_data_dir = browser_data_dir
        self.task_id = task_id
        self._retry_count = 0
        self._max_retries = 3
        self._base_delay = 1.0
        self._max_delay = 30.0
        self._exponential_base = 2.0

    def log_event(self, message: str, level: str = "info", **kwargs):
        """Log structured event with timestamp, task ID, and platform name.

        Args:
            message: Log message
            level: Log level (info, warning, error, etc.)
            **kwargs: Additional metadata to include in log
        """
        from datetime import UTC, datetime

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "message": message,
            "task_id": self.task_id,
            "platform": self.get_platform_name(),
            **kwargs,
        }
        getattr(logger, level)(f"{message} | platform={self.get_platform_name()} | task_id={self.task_id}")

    async def with_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff and retry logic.

        Args:
            func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self._max_retries):
            try:
                self._retry_count = attempt
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self._max_retries - 1:
                    raise
                delay = self._base_delay * (self._exponential_base ** attempt)
                delay = min(delay, self._max_delay)
                delay += random.uniform(0, 0.5)  # Add jitter
                self.log_event(
                    f"Attempt {attempt + 1}/{self._max_retries} failed: {str(e)}. Retrying in {delay:.2f}s",
                    level="warning",
                )
                await asyncio.sleep(delay)
        raise RuntimeError("Unexpected retry loop exit")

    @abstractmethod
    async def post(self, content: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Post content to the platform.

        Args:
            content: The content to post
            options: Platform-specific options (platform_name, tags, article_link, etc.)

        Returns:
            Dictionary with status and metadata

        Raises:
            Exception: If posting fails
        """
        pass

    @abstractmethod
    async def validate_auth(self) -> bool:
        """Validate authentication credentials.

        Returns:
            True if authenticated, False otherwise
        """
        pass
    @abstractmethod
    async def get_rate_limit_status(self) -> dict:
        """Get rate limit status for the platform.

        Returns:
            Dict with remaining, limit, and reset_time fields
        """
        pass

    async def random_delay(self, min_delay: float = 0.5, max_delay: float = 2.5):
        """Add a randomized delay to simulate human behavior.

        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

    async def normalize_content(self, content: str) -> str:
        """Normalize content before posting.

        Args:
            content: Raw content to normalize

        Returns:
            Normalized content
        """
        # Strip markdown formatting
        content = content.replace("# ", "").replace("* ", "").replace("- ", "")
        content = content.replace("**", "").replace("*", "")
        content = content.replace("`", "")
        content = content.replace("[", "").replace("]", "")
        content = content.replace("~", "")
        content = content.replace("\\", "")
        
        # Remove excessive whitespace
        import re
        content = re.sub(r"\s+", " ", content).strip()
        
        return content

    def get_platform_name(self) -> str:
        """Get the platform name for routing.

        Returns:
            Platform name in lowercase
        """
        return self.__class__.__name__.replace("Handler", "").lower()

    async def _create_browser_session(self) -> Any:
        """Create a browser session using BrowserProvider.
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
    ]
    # Randomly select a viewport
    selected_viewport = random.choice(viewports)

        Returns:
            Browser context

        Raises:
            Exception: If browser session creation fails
        """
        try:
            self.log_event("Starting browser session")
            async with BrowserProvider(self.browser_data_dir, task_id=self.task_id) as context:
                return context
        except Exception as e:
            self.log_event(f"Failed to create browser session: {str(e)}", level="error")
            raise

    async def _validate_session_health(self, page: Any, login_indicators: list | None = None) -> bool:
        """Validate session health and authentication status.

        Args:
            page: Browser page object
            login_indicators: Optional list of selectors to check for login indicators

        Returns:
            True if session is healthy, False otherwise
        """
        if login_indicators is None:
            login_indicators = [
                re.compile(r"Log in|Sign in|Join", re.IGNORECASE)
            ]

        try:
            login_indicators = await page.get_by_role(
                "link", name=login_indicators
            ).count()
            
            if login_indicators > 0:
                self.log_event("Session health check failed: Auth expired", level="error")
                return False
            
            self.log_event("Session health verified")
            return True
        except Exception as e:
            self.log_event(f"Session health check failed: {str(e)}", level="error")
            return False
