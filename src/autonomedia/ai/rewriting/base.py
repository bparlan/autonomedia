from abc import ABC, abstractmethod

class RewriteProvider(ABC):
    @abstractmethod
    async def rewrite(self, text: str, prompt: str) -> str:
        """Rewrite the text based on the provided prompt."""
        pass
