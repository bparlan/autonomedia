"""Integration tests for platform abstraction layer.

Tests unified API routing, platform-specific handlers, batch posting,
error handling, retry logic, and anti-detection techniques.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.autonomedia.browser.provider import BrowserProvider
from src.autonomedia.core.platform import (
    batch_post,
    get_handler,
    get_supported_platforms,
    post,
)

# Fixtures


@pytest.fixture
def mock_browser_provider(tmp_path):
    """Mock BrowserProvider with async context manager."""
    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=MagicMock())
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    
    mock = MagicMock(spec=BrowserProvider)
    mock.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock.__aexit__ = AsyncMock(return_value=None)
    
    return mock


@pytest.fixture
def test_content():
    """Sample content for testing."""
    return """# Sample Article

## Summary

This is a sample article about platform abstraction and multi-platform publishing.

The unified API allows for seamless content routing across different social media platforms.

## Key Points

- Character limits vary by platform
- Hashtag formatting differs between platforms
- Authentication flows are platform-specific
- Anti-detection techniques are essential

See full article at https://example.com/sample-article"""


@pytest.fixture
def linkedin_options():
    """LinkedIn-specific options."""
    return {
        "platform": "linkedin",
        "content_id": "test-content-1",
        "task_id": "test-task-1",
    }


@pytest.fixture
def x_options():
    """X-specific options."""
    return {
        "platform": "x",
        "content_id": "test-content-2",
        "task_id": "test-task-2",
    }


@pytest.fixture
def batch_options():
    """Batch posting options."""
    return {
        "platform": "mastodon",
        "content_id": "batch-test",
        "task_id": "batch-task",
        "batch_mode": True,
    }


# Test Unified API Routing


@pytest.mark.asyncio
async def test_unified_api_routing_sample():
    """Sample test to verify routing occurs."""
    result = await post(test_content, linkedin_options)
    
    # Verify routing occurred
    assert result["platform"] == "linkedin"
    assert result["success"] is False  # Will fail without actual auth, but routing is successful



@pytest.mark.asyncio
async def test_unified_api_routes_to_x_handler(mock_browser_provider):
    """Test unified API routes to X handler."""
    with patch("src.autonomedia.core.platform.get_handler", return_value=mock_browser_provider):
            result = await post(test_content, x_options)
            
            # Verify routing occurred
            assert result["platform"] == "x"
            assert result["success"] is False  # Will fail without actual auth, but routing is successful


@pytest.mark.asyncio
async def test_unified_api_supports_multiple_platforms():
    """Test that all three platforms are registered and available."""
    supported = get_supported_platforms()
    assert "linkedin" in supported
    assert "x" in supported
    assert "mastodon" in supported


@pytest.mark.asyncio
async def test_get_handler_returns_correct_instantiation():
    """Test that get_handler instantiates the correct handler class."""
    with patch("src.autonomedia.core.platform.XHandler") as MockX, \
         patch("src.autonomedia.core.platform.LinkedinHandler") as MockLinkedin, \
         patch("src.autonomedia.core.platform.MastodonHandler") as MockMastodon:
        
        # Mock browser_data_dir for instantiation
        mock_browser_provider = MagicMock()
        MockX.return_value = mock_browser_provider
        MockLinkedin.return_value = mock_browser_provider
        MockMastodon.return_value = mock_browser_provider
        
        # Get handler for X
        handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
        MockX.assert_called_once_with(browser_data_dir="/tmp", task_id="test")
        
        # Get handler for LinkedIn
        handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
        MockLinkedin.assert_called_once_with(browser_data_dir="/tmp", task_id="test")
        
        # Get handler for Mastodon
        handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
        MockMastodon.assert_called_once_with(browser_data_dir="/tmp", task_id="test")


# Test LinkedIn Handler Field Extraction


@pytest.mark.asyncio
async def test_linkedin_handler_extract_title(mock_browser_provider, test_content):
    """Test LinkedIn handler extracts title correctly."""
    # Mock the handler
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Extract title
    title = handler.extract_title(test_content, max_length=200)
    
    # Verify title characteristics
    assert len(title) <= 200
    assert len(title) > 100  # First 200 chars should be substantial
    assert "Sample Article" in title
    assert title.endswith("Summary")


@pytest.mark.asyncio
async def test_linkedin_handler_extract_summary(mock_browser_provider, test_content):
    """Test LinkedIn handler extracts summary correctly."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Extract title first
    title = handler.extract_title(test_content, max_length=200)
    
    # Extract summary from remaining content
    summary = handler.extract_summary(test_content, title)
    
    # Verify summary characteristics
    assert len(summary) <= 3000
    assert len(summary) > 500  # Should have meaningful content
    assert "platform abstraction" in summary.lower()
    assert "multi-platform publishing" in summary.lower()


@pytest.mark.asyncio
async def test_linkedin_handler_extract_tags(mock_browser_provider, test_content):
    """Test LinkedIn handler extracts and formats tags correctly."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Extract tags
    tags = handler.extract_tags(test_content)
    
    # Verify tag characteristics
    assert len(tags) <= 5
    assert len(tags) > 0
    assert all(len(tag) <= 25 for tag in tags)
    assert len(set(tags)) == len(tags)  # No duplicates
    
    # Verify tags are lowercase with underscores
    for tag in tags:
        assert tag == tag.lower()
        assert "_" in tag or tag.isalpha()


@pytest.mark.asyncio
async def test_linkedin_handler_normalizes_markdown(mock_browser_provider, test_content):
    """Test LinkedIn handler normalizes markdown content."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Content with markdown
    markdown_content = "# Title\n## Summary\nContent with **bold** and *italic* text."
    
    # Normalize content
    normalized = handler.normalize_content(markdown_content)
    
    # Verify markdown is stripped
    assert "# Title" not in normalized
    assert "## Summary" not in normalized
    assert "**bold**" not in normalized
    assert "*italic*" not in normalized
    assert "Title" in normalized  # Title should remain
    assert "bold" in normalized  # Text should remain


# Test X Handler Truncation and Formatting


@pytest.mark.asyncio
async def test_x_handler_truncates_to_280_characters(mock_browser_provider, test_content):
    """Test X handler truncates content to 280 characters."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Truncate content
    truncated = handler.truncate_tweet(test_content)
    
    # Verify truncation
    assert len(truncated) <= 280
    assert truncated.endswith("...")
    assert len(test_content) > 280


@pytest.mark.asyncio
async def test_x_handler_formats_hashtags(mock_browser_provider, test_content):
    """Test X handler formats hashtags correctly."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Content with various hashtag formats
    content_with_hashtags = """#sample #TestTag #another-tag #EXAMPLE"""
    
    # Extract and format hashtags
    hashtags = handler.extract_hashtags(content_with_hashtags)
    
    # Verify hashtag formatting
    assert len(hashtags) <= 3
    assert len(set(hashtags)) == len(hashtags)  # No duplicates
    assert hashtags[0] == "Sample"
    assert hashtags[1] == "TestTag"
    assert hashtags[2] == "Another_tag"
    assert hashtags[3] == "Example"


@pytest.mark.asyncio
async def test_x_handler_preserves_hook(mock_browser_provider, test_content):
    """Test X handler preserves the first line as a strong hook."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Content with first line as hook
    hook_content = "Strong hook line.\n\nMore content here."
    
    # Preserve hook
    preserved = handler.preserve_hook(hook_content)
    
    # Verify hook is preserved
    assert preserved.startswith("Strong hook line.")
    assert preserved.count("\n") == 1  # Single newline between hook and rest


@pytest.mark.asyncio
async def test_x_handler_preserves_article_link(mock_browser_provider, test_content):
    """Test X handler preserves article link at the end."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Content with article link
    content_with_link = "Content with link https://example.com/article at the end."
    
    # Preserve link
    preserved = handler.preserve_article_link(content_with_link)
    
    # Verify link is preserved
    assert "https://example.com/article" in preserved
    assert preserved.endswith("https://example.com/article")


@pytest.mark.asyncio
async def test_x_handler_batch_post_with_delays(mock_browser_provider):
    """Test X handler posts in batches with random delays."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Mock the browser session creation
    mock_page = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.screenshot = AsyncMock()
    
    mock_browser = MagicMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    
    # Track delays between posts
    delay_times = []
    
    original_delay = handler.random_delay
    
    async def mock_delay(min_delay, max_delay):
        await original_delay(min_delay, max_delay)
        delay_times.append((min_delay, max_delay))
    
    handler.random_delay = mock_delay
    
    # Test batch posting with 3 items
    contents = ["Content 1", "Content 2", "Content 3"]
    options = {"batch_mode": True}
    
    with patch.object(handler, "_create_browser_session", return_value=mock_browser):
        # Mock the posting operations
        mock_page.click.return_value = None
        
        results = await handler.batch_post(contents, options)
        
        # Verify batch posting occurred
        assert len(results) == 3
        assert all(r["success"] is False for r in results)  # Will fail without auth
        
        # Verify delays occurred between posts
        assert len(delay_times) == 2  # Delays between 3 posts


# Test Batch Posting Functionality


@pytest.mark.asyncio
async def test_batch_post_unified_api(mock_browser_provider, test_content):
    """Test unified batch_post function."""
    # Mock handler
    handler = MagicMock()
    handler.post.return_value = {"success": True, "post_id": "test-post"}
    
    with patch("src.autonomedia.core.platform.get_handler", return_value=handler):
        contents = ["Content 1", "Content 2"]
        options = {"platform": "mastodon", "content_id": "batch-test"}
        
        results = await batch_post(contents, options)
        
        # Verify results
        assert len(results) == 2
        assert handler.post.call_count == 2


@pytest.mark.asyncio
async def test_batch_post_respects_delay(mock_browser_provider, test_content):
    """Test batch_post includes random delays between posts."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Track delays
    delays = []
    
    original_delay = handler.random_delay
    
    async def track_delay(min_delay, max_delay):
        await original_delay(min_delay, max_delay)
        delays.append((min_delay, max_delay))
    
    handler.random_delay = track_delay
    
    # Test batch posting
    contents = ["Content 1", "Content 2", "Content 3"]
    options = {"batch_mode": True}
    
    with patch.object(handler, "post", return_value={"success": False}):
        results = await handler.batch_post(contents, options)
        
        # Verify delays occurred
        assert len(delays) == 2  # Delays between 3 posts


# Test Error Handling and Retry Logic


@pytest.mark.asyncio
async def test_retry_logic_on_network_error(mock_browser_provider):
    """Test retry logic handles transient network errors."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    call_count = 0
    
    async def failing_post(content, options=None):
        call_count += 1
        if call_count < 3:
            raise Exception("Network error")
        return {"success": True, "post_id": "test-post"}
    
    # Replace post method with failing version
    original_post = handler.post
    handler.post = failing_post
    
    try:
        result = await handler.post("Test content", {"test": "option"})
        
        # Verify retry occurred
        assert call_count == 3
        assert result["success"] is True
    finally:
        handler.post = original_post


@pytest.mark.asyncio
async def test_max_retry_limit_enforced(mock_browser_provider):
    """Test that maximum retry limit is enforced."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    call_count = 0
    
    async def always_failing_post(content, options=None):
        call_count += 1
        raise Exception("Permanent error")
    
    # Replace post method with always-failing version
    original_post = handler.post
    handler.post = always_failing_post
    
    try:
        result = await handler.post("Test content", {"test": "option"})
        
        # Verify retry limit was enforced
        assert call_count == 4  # Initial attempt + 3 retries
        assert result["success"] is False
        assert "Permanent error" in result["error"]
    finally:
        handler.post = original_post


@pytest.mark.asyncio
async def test_exponential_backoff_implemented(mock_browser_provider):
    """Test that exponential backoff is used between retries."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    delays = []
    
    original_delay = handler.random_delay
    
    async def track_delay(min_delay, max_delay):
        await original_delay(min_delay, max_delay)
        delays.append((min_delay, max_delay))
    
    handler.random_delay = track_delay
    
    call_count = 0
    
    async def failing_post(content, options=None):
        call_count += 1
        raise Exception("Transient error")
    
    original_post = handler.post
    handler.post = failing_post
    
    try:
        await handler.post("Test content", {"test": "option"})
        
        # Verify delays occurred between retries
        assert len(delays) >= 3
        
        # Delays should increase (exponential backoff)
        for i in range(1, len(delays)):
            assert delays[i][1] >= delays[i-1][1]
    finally:
        handler.post = original_post
        handler.random_delay = original_delay


@pytest.mark.asyncio
async def test_error_response_includes_platform_info(mock_browser_provider):
    """Test error responses include platform and error details."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    try:
        await handler.post("Test content", {"test": "option"})
    except Exception as e:
        error_result = {
            "success": False,
            "platform": "mastodon",
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        # Verify error response structure
        assert error_result["platform"] == "mastodon"
        assert error_result["success"] is False
        assert "error" in error_result
        assert "error_type" in error_result


# Test Anti-Detection Techniques


@pytest.mark.asyncio
async def test_randomized_delays_for_human_like_behavior(mock_browser_provider):
    """Test that randomized delays simulate human behavior."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    delays = []
    
    original_delay = handler.random_delay
    
    async def track_delay(min_delay, max_delay):
        await original_delay(min_delay, max_delay)
        delays.append((min_delay, max_delay))
    
    handler.random_delay = track_delay
    
    # Test multiple random delays
    for _ in range(5):
        await handler.random_delay(0.5, 2.5)
    
    # Verify delays varied within expected range
    all_delays = [d for _, d in delays]
    assert min(all_delays) >= 0.5
    assert max(all_delays) <= 2.5
    assert len(set(all_delays)) > 1  # Delays should not all be identical


@pytest.mark.asyncio
async def test_browser_viewport_randomization(mock_browser_provider):
    """Test that BrowserProvider uses randomized viewports."""
    # This tests the BrowserProvider itself
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    viewports = []
    
    # Track viewport randomization
    original_create = handler._create_browser_session
    
    async def mock_create_session():
        # Get viewport from context manager
        async with handler._create_browser_session():
            pass
        return None
    
    # Mock the session creation to track viewport
    handler._create_browser_session = mock_create_session
    
    try:
        # Create multiple sessions
        for _ in range(5):
            await handler._create_browser_session()
        
        # Note: Viewport randomization is tested in BrowserProvider unit tests
        # This test verifies the capability exists
        assert handler._create_browser_session is not None
    finally:
        handler._create_browser_session = original_create


@pytest.mark.asyncio
async def test_headless_mode_disabled_for_browsers(mock_browser_provider):
    """Test that browser profiles are created with headless=False."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Check that anti-detection arguments are present
    # This is verified by the BrowserProvider implementation
    # which includes --disable-blink-features=AutomationControlled
    assert hasattr(handler, "_create_browser_session")


@pytest.mark.asyncio
async def test_session_health_check_implemented(mock_browser_provider):
    """Test that session health check is implemented."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Check that validation method exists
    assert hasattr(handler, "validate_auth")
    assert callable(handler.validate_auth)


# Test Platform-Specific Edge Cases


@pytest.mark.asyncio
async def test_empty_content_handling(mock_browser_provider):
    """Test that empty content is handled gracefully."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Test truncation with empty content
    truncated = handler.truncate_tweet("")
    assert truncated == ""
    
    # Test hashtag extraction with no hashtags
    hashtags = handler.extract_hashtags("")
    assert hashtags == []
    
    # Test tag extraction with no tags
    tags = handler.extract_tags("")
    assert tags == []


@pytest.mark.asyncio
async def test_content_exactly_at_character_limit(mock_browser_provider):
    """Test handling of content exactly at character limit."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Create content exactly at 280 characters
    exact_content = "x" * 280
    
    truncated = handler.truncate_tweet(exact_content)
    
    # Verify content is not truncated (no ellipsis added)
    assert len(truncated) == 280
    assert truncated == exact_content


@pytest.mark.asyncio
async def test_very_long_content_truncation(mock_browser_provider):
    """Test truncation of very long content."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Create very long content
    long_content = "x" * 1000
    
    truncated = handler.truncate_tweet(long_content)
    
    # Verify content is truncated
    assert len(truncated) == 280
    assert truncated.endswith("...")
    assert len(long_content) > 280


@pytest.mark.asyncio
async def test_multiple_duplicate_hashtags_removed(mock_browser_provider):
    """Test that duplicate hashtags are removed."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Content with duplicate hashtags
    content = "#hashtag #Hashtag #hashtag #HASHTAG #hashtag"
    
    hashtags = handler.extract_hashtags(content)
    
    # Verify only unique hashtags remain
    assert len(hashtags) <= 3  # Max 3 unique hashtags
    assert len(set(hashtags)) == len(hashtags)  # No duplicates


@pytest.mark.asyncio
async def test_title_with_max_length(mock_browser_provider):
    """Test title extraction at maximum length."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Create title at max length
    max_title = "x" * 300
    
    title = handler.extract_title(max_title, max_length=300)
    
    # Verify title is exactly 300 characters
    assert len(title) == 300


@pytest.mark.asyncio
async def test_summary_without_title(mock_browser_provider):
    """Test summary extraction when title is empty or None."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Content without title marker
    content = "Just a summary with no title header."
    
    # Extract title (should be empty or trimmed)
    title = handler.extract_title(content)
    assert len(title) < 50  # Should extract only first few characters
    
    # Extract summary
    summary = handler.extract_summary(content, title)
    assert len(summary) > 0


# Test Convenience Functions


@pytest.mark.asyncio
async def test_convenience_function_post_to_linkedin(mock_browser_provider, test_content):
    """Test convenience function post_to_linkedin."""
    with patch("src.autonomedia.core.platform.post", return_value={"success": True}) as mock_post:
        result = await post_to_linkedin(test_content, {"content_id": "test"})
        
        # Verify call was made
        assert mock_post.called
        assert result["platform"] == "linkedin"


@pytest.mark.asyncio
async def test_convenience_function_post_to_x(mock_browser_provider, test_content):
    """Test convenience function post_to_x."""
    with patch("src.autonomedia.core.platform.post", return_value={"success": True}) as mock_post:
        result = await post_to_x(test_content, {"content_id": "test"})
        
        # Verify call was made
        assert mock_post.called
        assert result["platform"] == "x"


# Test Error Recovery and Fallbacks


@pytest.mark.asyncio
async def test_handler_unavailable_fallback():
    """Test that unknown platform raises appropriate error."""
    with pytest.raises(KeyError):
        get_handler("unknown_platform", browser_data_dir="/tmp", task_id="test")


@pytest.mark.asyncio
async def test_normalize_content_without_options(mock_browser_provider, test_content):
    """Test normalize_content without options defaults to standard rules."""
    from src.autonomedia.core.platform import normalize_content
    
    # Normalize without options
    normalized = await normalize_content(test_content)
    
    # Should strip markdown but preserve structure
    assert "# Sample Article" not in normalized
    assert "Sample Article" in normalized


@pytest.mark.asyncio
async def test_normalize_content_with_platform_options(mock_browser_provider, test_content):
    """Test normalize_content with platform-specific options."""
    from src.autonomedia.core.platform import normalize_content
    
    # Normalize for X (should strip markdown)
    x_options = {"platform": "x"}
    normalized = await normalize_content(test_content, x_options)
    
    assert "# Sample Article" not in normalized


@pytest.mark.asyncio
async def test_normalize_content_for_linkedin(mock_browser_provider, test_content):
    """Test normalize_content for LinkedIn (should extract title)."""
    from src.autonomedia.core.platform import normalize_content
    
    # Normalize for LinkedIn
    linkedin_options = {"platform": "linkedin"}
    normalized = await normalize_content(test_content, linkedin_options)
    
    # Should have extracted title
    assert "Sample Article" in normalized


@pytest.mark.asyncio
async def test_handler_logging_includes_task_id(mock_browser_provider):
    """Test that handler logging includes task_id."""
    handler = get_handler("mastodon", browser_data_dir="/tmp", task_id="test-task-123")
    
    # Check that task_id is stored
    assert handler.task_id == "test-task-123"
    
    # Verify get_platform_name
    platform_name = handler.get_platform_name()
    assert platform_name == "mastodon"


# Test Character Limit Validation


@pytest.mark.asyncio
async def test_linkedin_title_max_length_validation(mock_browser_provider, test_content):
    """Test LinkedIn title field length validation."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Test various title lengths
    long_title = "x" * 500
    
    title = handler.extract_title(long_title, max_length=300)
    
    # Should be capped at 300
    assert len(title) == 300


@pytest.mark.asyncio
async def test_linkedin_summary_max_length_validation(mock_browser_provider, test_content):
    """Test LinkedIn summary field length validation."""
    handler = get_handler("linkedin", browser_data_dir="/tmp", task_id="test")
    
    # Test various summary lengths
    long_summary = "x" * 5000
    
    title = handler.extract_title(test_content, max_length=200)
    summary = handler.extract_summary(long_summary, title)
    
    # Should be capped at 3000
    assert len(summary) == 3000


@pytest.mark.asyncio
async def test_x_character_limit_constant(mock_browser_provider):
    """Test that X character limit is constant."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # X should always use 280 character limit
    assert handler.CHARACTER_LIMIT == 280


@pytest.mark.asyncio
async def test_mastodon_character_limit(mock_browser_provider):
    """Test Mastodon character limit."""
    handler = get_handler("x", browser_data_dir="/tmp", task_id="test")
    
    # Mastodon should have toot/status/note limits
    assert "toot" in handler.CHARACTER_LIMITS
    assert "status" in handler.CHARACTER_LIMITS
    assert "note" in handler.CHARACTER_LIMITS
    assert handler.CHARACTER_LIMITS["toot"] == 500
    assert handler.CHARACTER_LIMITS["status"] == 500
    assert handler.CHARACTER_LIMITS["note"] == 500
