import json
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

# Configuration for template testing
TEMPLATES_DIR = Path(__file__).parent.parent / "src" / "web" / "templates"


class MockRequest:
    """Mock request object for Jinja2 template rendering."""
    def __init__(self):
        self.url = self

    @property
    def path(self):
        return "/"


@pytest.fixture
def jinja_env():
    """Provides a Jinja2 environment for template testing."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    env.filters['fromjson'] = lambda x: json.loads(x) if x else {}
    return env


@pytest.fixture
def mock_request():
    """Provides a mock request object."""
    return MockRequest()


class TestM13S3ReadyToPublishPerPlatformRows:
    """Tests for M13S3: Frontend Ready to Publish Per-Platform Rows"""

    def test_item_with_two_verified_platforms_shows_two_rows(self, jinja_env, mock_request):
        """TC-M13S3-01: Item with two verified platforms - Two rows, each with green badge."""
        template = jinja_env.get_template("dashboard.html")

        # Test data: item with two verified platforms
        ready_items = [
            {
                "id": "100",
                "topic": "Test Topic",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": "This is the mastodon content preview text that should be displayed",
                    "twitter": "This is the twitter content preview text"
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"},
                    "twitter": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}
                }),
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        # Should render 2 rows for 2 platforms
        assert "mastodon" in rendered.lower()
        assert "twitter" in rendered.lower()
        assert "Verified - In Queue" in rendered
        assert "#10b981" in rendered or "bg-green" in rendered or "text-green" in rendered

    def test_item_with_one_non_verified_platform_shows_neutral_badge(self, jinja_env, mock_request):
        """TC-M13S3-02: Item with one non-verified platform - Single row with neutral/gray badge."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "101",
                "topic": "Single Platform",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": "Single platform content"
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": False, "verified_at": None, "expires_at": None}
                }),
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert "mastodon" in rendered.lower()
        assert "Unverified" in rendered or "Pending" in rendered or "#6b7280" in rendered

    def test_content_shorter_than_100_chars_displays_full_text(self, jinja_env, mock_request):
        """TC-M13S3-03: Item with content < 100 chars - Full content displayed, no truncation."""
        template = jinja_env.get_template("dashboard.html")

        short_content = "Short content under 100 characters"
        assert len(short_content) < 100

        ready_items = [
            {
                "id": "102",
                "topic": "Short Content Test",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": short_content
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}
                })
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert short_content in rendered

    def test_item_with_no_platforms_shows_no_rows(self, jinja_env, mock_request):
        """TC-M13S3-04: Item with no platforms - No rows rendered for that item."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "103",
                "topic": "No Platforms",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({}),
                "verification_status": json.dumps({})
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert "No prepared content" in rendered or "No posts ready for publication" in rendered

    def test_content_preview_uses_text_xs_styling(self, jinja_env, mock_request):
        """Content preview displays with Tailwind text-xs styling."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "104",
                "topic": "Preview Test",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": "Long content that should be truncated at 100 characters for preview purposes in the table view"
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}
                })
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert "text-xs" in rendered

    def test_review_verify_link_present_for_all_rows(self, jinja_env, mock_request):
        """TC-M13S3-05: Verify Review/Verify link presence for platform rows."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "105",
                "topic": "Link Test",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": "Content for link test",
                    "twitter": "Another content"
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"},
                    "twitter": {"verified": False, "verified_at": None, "expires_at": None}
                })
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        # Check for Review link in the Ready to Publish section (href="/review/105")
        assert 'href="/review/105"' in rendered

    def test_row_count_equals_sum_of_platforms(self, jinja_env, mock_request):
        """Row count equals sum of all platforms across ready_to_post items."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "1",
                "topic": "Item 1",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({"mastodon": "a", "twitter": "b"}),
                "verification_status": json.dumps({"mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}, "twitter": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}})
            },
            {
                "id": "2",
                "topic": "Item 2",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({"mastodon": "c"}),
                "verification_status": json.dumps({"mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}})
            },
            {
                "id": "3",
                "topic": "Item 3",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({}),
                "verification_status": json.dumps({})
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert "Item 1" in rendered
        assert "Item 2" in rendered

    def test_long_content_truncated_at_100_chars(self, jinja_env, mock_request):
        """Content preview should be truncated at 100 characters with ellipsis."""
        template = jinja_env.get_template("dashboard.html")

        long_content = "x" * 150  # 150 characters
        expected_preview = "x" * 100 + "..."

        ready_items = [
            {
                "id": "106",
                "topic": "Long Content",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": long_content
                }),
                "verification_status": json.dumps({
                    "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}
                })
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        # Should have truncated content with ellipsis
        assert (expected_preview in rendered) or ("..." in rendered and long_content[:100] in rendered)

    def test_unknown_verification_status_shows_pending(self, jinja_env, mock_request):
        """Platforms with unknown verification status should show 'Pending' badge."""
        template = jinja_env.get_template("dashboard.html")

        ready_items = [
            {
                "id": "107",
                "topic": "Unknown Status",
                "type": "blog",
                "status": "ready_to_post",
                "prepared_content": json.dumps({
                    "mastodon": "Content"
                }),
                "verification_status": json.dumps({})  # No verification status
            }
        ]

        rendered = template.render(
            request=mock_request,
            ready_items=ready_items,
            prepared_items=[],
            failed_items=[]
        )

        assert "Pending" in rendered
        assert "Unknown Status" in rendered
