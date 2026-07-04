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

    def __init__(self, browser_data_dir: str, task_id: str = None):
        self.browser_data_dir = browser_data_dir
        self.task_id = task_id
        self.context = None
        self.playwright = None

    def _get_random_viewport(self):
        """Randomizes viewport to avoid consistent fingerprinting."""
        widths = [1280, 1366, 1440, 1600, 1920]
        heights = [720, 768, 900, 1080]
        return {"width": random.choice(widths), "height": random.choice(heights)}

    async def _human_delay(self):
        """Randomized delay to simulate human timing."""
        await asyncio.sleep(random.uniform(0.5, 2.5))

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        viewport = self._get_random_viewport()
        logger.info(f"Launching browser with viewport {viewport}")

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.browser_data_dir,
            headless=False,
            viewport=viewport,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )
        return self.context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Artifact capture on failure
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
