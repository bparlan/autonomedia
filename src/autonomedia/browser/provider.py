import asyncio
import logging
import random

from playwright.async_api import async_playwright

logger = logging.getLogger("browser_provider")


class BrowserProvider:
    """
    Centralized Browser Provider for context management,
    lifecycle, and consistent artifact capture.
    Includes BrowserProfiling for randomization to reduce bot detection.
    """

    def __init__(self, browser_data_dir: str, task_id: str = None, user_agent: str = None):
        self.browser_data_dir = browser_data_dir
        self.task_id = task_id
        self.user_agent = user_agent if user_agent else self._get_random_user_agent() # Store user agent or pick random
        self.context = None
        self.playwright = None

    def _get_random_viewport(self):
            """Randomizes viewport to avoid consistent fingerprinting."""
            viewports = [
                {"width": 1920, "height": 1080},
                {"width": 1366, "height": 768},
                {"width": 1536, "height": 864},
            ]
            return random.choice(viewports)

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def _get_random_user_agent(self):
        """Selects a random user agent from the predefined list."""
        return random.choice(self.USER_AGENTS)

    async def _human_delay(self):
        """Randomized delay to simulate human timing."""
        await asyncio.sleep(random.uniform(0.5, 2.5))

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        viewport = self._get_random_viewport()
        logger.info(f"Launching browser with viewport {viewport}")

        # Determine the user agent to use. If self.user_agent is None, use a random one.
        final_user_agent = self.user_agent
        if not final_user_agent:
            final_user_agent = self._get_random_user_agent()

        logger.info(f"Launching browser with viewport {viewport} and user agent {final_user_agent}")

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.browser_data_dir,
            headless=False,
            viewport=viewport,
            user_agent=final_user_agent,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )
        return self.context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Note: Removed the incorrect 'user_agent=selected_user_agent' line here.
            await self._capture_failure(exc_val)

        await self.context.close()
        await self.playwright.stop()

    async def _capture_failure(self, exception):
        """Captures screenshots and logs on failure."""
        if self.task_id and self.context and self.context.pages:
            screenshot_path = f"storage/screenshots/{self.task_id}_failure.png"
            await self.context.pages[0].screenshot(path=screenshot_path)
            logger.error(
                f"Captured failure artifacts for {self.task_id} at {screenshot_path}"
            )
        else:
            logger.error(f"Failed to capture artifacts: {exception}")
