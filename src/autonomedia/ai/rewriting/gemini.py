import os
import asyncio
import logging
from google import genai
from .base import RewriteProvider

logger = logging.getLogger(__name__)

# List confirmed available by your API key
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3-flash-preview",
]

class GeminiProvider(RewriteProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) must be set in environment")
        
        self.client = genai.Client(api_key=self.api_key)

    async def rewrite(self, text: str, prompt: str) -> str:
        loop = asyncio.get_running_loop()
        last_error = None
        full_prompt = f"{prompt}\n\nOriginal Text:\n{text}"

        for model in FALLBACK_MODELS:
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda m=model: self.client.models.generate_content(
                        model=m,
                        contents=full_prompt
                    )
                )
                return response.text

            except Exception as e:
                # Inspect for status codes 404 (model gone) or 429 (rate limited)
                status = getattr(e, 'status_code', None)
                err_str = str(e)
                
                # Check status code or string representation for 404/429
                if status in (404, 429) or "404" in err_str or "429" in err_str:
                    logger.warning(f"Model {model} failed ({status or 'Unknown'}). Falling back...")
                    last_error = e
                    continue
                
                # Fail fast on Auth (401/403) or Malformed requests
                logger.error(f"Critical AI error: {e}")
                raise e

        raise RuntimeError(
            f"All Gemini models exhausted. Final error: {last_error}"
        )
