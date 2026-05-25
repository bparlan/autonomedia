import pytest
from src.autonomedia.ai.rewriting.context import RewriteContext
from src.autonomedia.ai.rewriting.gemini import GeminiProvider

@pytest.mark.asyncio
async def test_rewrite_context_serialization():
    ctx = RewriteContext(
        source_idea="Test idea",
        tags=["#test"],
        mentions=["@test"],
        url="http://test.com",
        platform="mastodon"
    )
    prompt = ctx.to_prompt_block()
    assert "Platform: mastodon" in prompt
    assert "Test idea" in prompt
    assert "#test" in prompt
    assert "http://test.com" in prompt

# Note: Integration with actual AI is excluded from unit tests, 
# relying on mocks or golden master for regression.
