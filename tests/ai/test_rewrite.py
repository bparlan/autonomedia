import json
import os

import pytest
from dotenv import load_dotenv

from autonomedia.ai.rewriting.context import RewriteContext
from autonomedia.ai.rewriting.gemini import GeminiProvider

# Load environment variables from .env
load_dotenv()

# Load fixtures
with open("tests/fixtures/rewrite/golden_master.json") as f:
    fixtures = json.load(f)

@pytest.mark.xfail(reason="Gemini API 503 errors (high demand)")
@pytest.mark.asyncio
async def test_rewrite_golden_master():
    # Initialize provider
    # Note: Requires GEMINI_API_KEY env var
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    provider = GeminiProvider(api_key=api_key)

    for item in fixtures:
        context = RewriteContext(source_idea=item["input"]["text"])
        try:
            result = await provider.rewrite(
                context=context,
                prompt=item["input"]["prompt"]
            )
        except RuntimeError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                pytest.skip(f"Gemini API spending limit exceeded: {e}")
            raise e

        # Golden Master Verification
        # We verify that the output contains the expected critical fragment
        assert item["expected_output_fragment"] in result, \
            f"Rewrite for {item['id']} failed to include critical content: {item['expected_output_fragment']}"

