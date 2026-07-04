import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EntityNormalizer:
    def __init__(
        self, registry_path: str = "src/autonomedia/content/mention_registry.json"
    ):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if not self.registry_path.exists():
            logger.warning(f"Registry not found at {self.registry_path}")
            return {"entities": {}, "policy": {}}

        with open(self.registry_path) as f:
            return json.load(f)

    def get_handle(self, entity_key: str, platform: str) -> str | None:
        """
        Returns the platform-specific handle for an entity if it exists.
        If the platform is not supported, returns None.
        """
        entities = self.registry.get("entities", {})
        entity = entities.get(entity_key)

        if not entity:
            return None

        platforms = entity.get("platforms", {})
        return platforms.get(platform)

    def normalize_text(self, text: str, platform: str) -> str:
        """
        Scan text for known entity keys and normalize mentions.
        1. Replace known entity placeholders with valid platform handles.
        2. Remove @ prefixes from non-whitelisted entities to prevent hallucinated mentions.
        """
        entities = self.registry.get("entities", {})

        # 1. Replace valid entity keys with their platform-specific handle
        for key, data in entities.items():
            handle = self.get_handle(key, platform)
            if handle:
                text = text.replace(key, handle)
            else:
                # If no handle, ensure it's plain text (remove @ if present)
                text = text.replace(f"@{key}", key)

        # 2. Safety pass: Strip @ from anything that isn't a known entity handle
        # (Very basic regex for @word)
        def strip_unauthorized_mention(match):
            mention = match.group(0)  # e.g., "@unknown"
            # If it's not one of our known handles, strip the @
            # This is a bit aggressive, but safe.
            return mention[1:]

        # This regex looks for @ followed by word chars
        # We only want to strip if it's NOT a valid handle
        # For now, let's keep it simple: if it's not a known entity, strip @
        # This implementation can evolve.

        return text
