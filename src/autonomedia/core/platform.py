"""Platform registry and browser provider wrapper."""
import asyncio
import logging
import os
import random
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger("autonomedia.platform")

# Use existing handlers from the original codebase
from autonomedia.platforms.mastodon.task_handler import MastodonHandler as MastodonHandlerOriginal
from autonomedia.platforms.linkedin.task_handler import LinkedInHandler as LinkedInHandlerOriginal
from autonomedia.platforms.x.task_handler import XHandler as XHandlerOriginal

class PlatformHandler:
    """Abstract platform handler."""

    def __init__(self, browser_data_dir: str, task_id: Optional[str] = None):
        self.browser_data_dir = browser_data_dir
        self.task_id = task_id
        self.platform = self.__class__.__name__.lower().replace("handler", "")

    async def post(self, content: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

    async def validate_auth(self) -> bool:
        raise NotImplementedError

    async def get_rate_limit_status(self) -> Dict[str, Any]:
        return {"platform": self.platform, "remaining": None, "limit": None}

    async def random_delay(self, min_delay: float = 0.5, max_delay: float = 2.5):
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

    def log_event(self, message: str, level: str = "info", **kwargs):
        entry = {"timestamp": self._now(), "level": level, "message": message, "platform": self.platform, "task_id": self.task_id, **kwargs}
        getattr(logger, level)(json.dumps(entry))

    def _now(self):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    async def capture_screenshot(self, page: Page, path: str):
        await page.screenshot(path=path, type="png")


class PlaywrightProvider:
    """Manages Playwright browser sessions per platform."""

    def __init__(self, browser_data_dir: str, platform_name: str):
        self.browser_data_dir = Path(browser_data_dir) / platform_name
        self.platform_name = platform_name
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.user_agent = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
        )
        self.page = await self.context.new_page()
        logger.info(f"Started browser for platform {self.platform_name}")

    async def stop(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info(f"Stopped browser for platform {self.platform_name}")

    async def goto(self, url: str):
        await self.page.goto(url)

    async def fill(self, selector: str, text: str):
        await self.page.fill(selector, text)

    async def click(self, selector: str):
        await self.page.click(selector)

    async def wait_for_selector(self, selector: str, timeout: float = 5000):
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def screenshot(self, path: str):
        await self.page.screenshot(path=path)

    async def close(self):
        if self.context:
            await self.context.close()


class PlatformRegistry:
    """Register and retrieve platform handlers."""

    def __init__(self, profiles_dir: str):
        self.profiles_dir = Path(profiles_dir)
        self.handlers = {}
        self.providers = {}
        self._load_handlers()

    def _load_handlers(self):
        # Use the original handlers
        self.handlers = {
            "mastodon": MastodonHandlerOriginal,
            "linkedin": LinkedInHandlerOriginal,
            "x": XHandlerOriginal,
        }
        for name in self.handlers:
            profile_dir = self.profiles_dir / name
            profile_dir.mkdir(parents=True, exist_ok=True)
            self.providers[name] = PlaywrightProvider(str(profile_dir), name)
        logger.info(f"Loaded platform handlers: {list(self.handlers.keys())}")

    def get_handler_class(self, platform: str) -> Optional[Any]:
        return self.handlers.get(platform.lower())

    def get_provider(self, platform: str) -> Optional[PlaywrightProvider]:
        return self.providers.get(platform.lower())

    async def start_provider(self, platform: str) -> bool:
        provider = self.get_provider(platform)
        if provider:
            await provider.start()
            return True
        logger.error(f"No provider for platform {platform}")
        return False

    async def stop_provider(self, platform: str):
        provider = self.get_provider(platform)
        if provider:
            await provider.stop()

    async def get_page(self, platform: str) -> Optional[Page]:
        provider = self.get_provider(platform)
        return provider.page if provider else None

    async def navigate(self, platform: str, url: str):
        provider = self.get_provider(platform)
        if provider:
            await provider.goto(url)

    async def fill(self, platform: str, selector: str, text: str):
        provider = self.get_provider(platform)
        if provider:
            await provider.fill(selector, text)

    async def click(self, platform: str, selector: str):
        provider = self.get_provider(platform)
        if provider:
            await provider.click(selector)

    async def screenshot(self, platform: str, path: str):
        provider = self.get_provider(platform)
        if provider:
            await provider.screenshot(path)
