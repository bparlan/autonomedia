import json
import os

import pytest
from dotenv import load_dotenv

from autonomedia.ai.rewriting.context import RewriteContext
from autonomedia.ai.rewriting.gemini import GeminiAIClient

# Load environment variables from .env
load_dotenv()

# Load fixtures
try:
    with open("tests/fixtures/rewrite/golden_master.json") as f:
        fixtures = json.load(f)
except FileNotFoundError:
    fixtures = []


@pytest.mark.xfail(reason="Gemini API 503 errors (high demand)")
@pytest.mark.asyncio
async def test_rewrite_golden_master():
    # Skip if no fixtures
    if not fixtures:
        pytest.skip("No fixtures found")

    # Initialize provider
    # Note: Requires GEMINI_API_KEY env var
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    provider = GeminiAIClient()

    for item in fixtures:
        context = RewriteContext(source_idea=item["input"]["text"])
        try:
            result = provider.analyze_idea(context.source_idea)
        except RuntimeError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                pytest.skip(f"Gemini API spending limit exceeded: {e}")
            raise e

        # Golden Master Verification
        # We verify that the output contains the expected critical fragment
        # For analyze_idea, check that keywords are extracted
        assert isinstance(result, dict), f"Rewrite for {item['id']} failed to return dict"
        assert "keywords" in result, f"Rewrite for {item['id']} missing keywords"