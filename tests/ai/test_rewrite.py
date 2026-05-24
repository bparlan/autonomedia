import pytest
import json
import os
from dotenv import load_dotenv
from autonomedia.ai.rewriting.gemini import GeminiProvider

# Load environment variables from .env
load_dotenv()

# Load fixtures
with open("tests/fixtures/rewrite/golden_master.json", "r") as f:
    fixtures = json.load(f)

@pytest.mark.asyncio
async def test_rewrite_golden_master():
    # Initialize provider
    # Note: Requires GEMINI_API_KEY env var
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    provider = GeminiProvider(api_key=api_key)

    for item in fixtures:
        result = await provider.rewrite(
            text=item["input"]["text"],
            prompt=item["input"]["prompt"]
        )
        
        # Golden Master Verification
        # We verify that the output contains the expected critical fragment
        assert item["expected_output_fragment"] in result, \
            f"Rewrite for {item['id']} failed to include critical content: {item['expected_output_fragment']}"

        print(f"Verified {item['id']}: {result[:50]}...")
