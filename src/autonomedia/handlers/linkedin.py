"""Wrapper to use existing LinkedInHandler."""
import logging
from typing import Any
from autonomedia.platforms.linkedin.task_handler import LinkedInHandler as OriginalHandler

logger = logging.getLogger("autonomedia.handlers.linkedin")

class LinkedInHandler:
    def __init__(self, browser_data_dir: str, task_id: str | None = None, auth_token: str | None = None):
        self._original = OriginalHandler(browser_data_dir, task_id, auth_token)

    async def validate_auth(self) -> bool:
        return await self._original.validate_auth()

    async def post(self, content: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._original.post(content, options)
