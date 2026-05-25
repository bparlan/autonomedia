from abc import ABC, abstractmethod
from .context import RewriteContext

class RewriteProvider(ABC):
    @abstractmethod
    async def rewrite(self, context: RewriteContext, prompt: str) -> str:
        """Rewrite the text based on the provided prompt and structured context."""
        pass
