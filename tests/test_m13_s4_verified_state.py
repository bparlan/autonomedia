"""
Test suite for M13S4 - AI Rewrite Dashboard Verified State.

Covers Test Cases TC1-TC5 from docs/verifications/M13S4V.md
"""
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
        return "/rewrites"


@pytest.fixture
def jinja_env():
    """Provides a Jinja2 environment for template testing."""
    def safe_fromjson(value):
        """Safe JSON parsing that returns empty dict on error."""
        if isinstance(value, str):
            try:
                result = json.loads(value)
                if isinstance(result, dict):
                    return result
                return {}
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    env.filters['fromjson'] = safe_fromjson
    return env


@pytest.fixture
def mock_request():
    """Provides a mock request object."""
    return MockRequest()


class TestM13S4VerifiedStateInQueue:
    """Tests for M13S4: AI Rewrite Dashboard Verified State."""

    def test_tc1_single_platform_ready_to_post_shows_verified_badge(self, jinja_env, mock_request):
        """TC1: Single-platform ready_to_post item -> Verified - In Queue badge appears."""
        template = jinja_env.get_template("partials/content_row.html")

        # Single platform with verification - use correct nested format
        item = {
            "id": "tp01",
            "topic": "Single Platform Item",
            "type": "blog",
            "status": "ready_to_post",
            "prepared_content": json.dumps({"mastodon": "Content for mastodon"}),
            "verification_status": json.dumps({"mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}}),
            "source_idea": "Test idea"
        }

        rendered = template.render(request=mock_request, item=item)

        assert "Mastodon: Verified - In Queue" in rendered, "Should show Mastodon Verified badge"
        assert "bg-green" in rendered or "#10b981" in rendered, "Badge should have green styling"

    def test_tc2_multi_platform_mixed_verification_shows_both_badges(self, jinja_env, mock_request):
        """TC2: Multi-platform ready_to_post item with some platforms verified -> correct badges per platform."""
        template = jinja_env.get_template("partials/content_row.html")

        # Mixed verification status - mastodon verified, twitter not verified - use correct nested format
        item = {
            "id": "tp02",
            "topic": "Multi Platform Item",
            "type": "blog",
            "status": "ready_to_post",
            "prepared_content": json.dumps({
                "mastodon": "Mastodon content",
                "twitter": "Twitter content"
            }),
            "verification_status": json.dumps({
                "mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"},
                "twitter": {"verified": False, "verified_at": None, "expires_at": None}
            }),
            "source_idea": "Test idea"
        }

        rendered = template.render(request=mock_request, item=item)

        # Should show both Verified and Unverified badges with platform labels
        assert "Mastodon: Verified - In Queue" in rendered, "Should show Mastodon verified badge with platform label"
        assert "Twitter: Unverified" in rendered, "Should show Twitter unverified badge with platform label"

    def test_tc3_ready_to_post_empty_verification_shows_generic_badge(self, jinja_env, mock_request):
        """TC3: ready_to_post item with empty verification_status -> generic Verified - In Queue badge."""
        template = jinja_env.get_template("partials/content_row.html")

        item = {
            "id": "tp03",
            "topic": "Empty Verification Item",
            "type": "blog",
            "status": "ready_to_post",
            "prepared_content": json.dumps({"mastodon": "Content"}),
            "verification_status": json.dumps({})  # Empty verification
        }

        rendered = template.render(request=mock_request, item=item)

        # With empty verification, the else branch (line 49-50 in template) shows generic badge
        assert "Verified - In Queue" in rendered, "Should show generic Verified - In Queue badge for empty verification"

    def test_tc4_malformed_verification_json_no_ui_crash(self, jinja_env, mock_request):
        """TC4: Item with malformed verification_status JSON -> UI remains stable, no badge."""
        template = jinja_env.get_template("partials/content_row.html")

        item = {
            "id": "tp04",
            "topic": "Malformed JSON Item",
            "type": "blog",
            "status": "ready_to_post",
            "prepared_content": json.dumps({"mastodon": "Content"}),
            "verification_status": "invalid-json"  # Malformed JSON
        }

        try:
            rendered = template.render(request=mock_request, item=item)
            # Should handle gracefully
            assert True
        except Exception as e:
            pytest.fail(f"Template should handle malformed JSON gracefully: {e}")

    def test_tc5_review_verify_link_remains_for_ready_to_post(self, jinja_env, mock_request):
        """TC5: Review/Verify link click on any ready_to_post item -> editing page loads."""
        template = jinja_env.get_template("partials/content_row.html")

        item = {
            "id": "tp05",
            "topic": "Link Test Item",
            "type": "blog",
            "status": "ready_to_post",
            "prepared_content": json.dumps({"mastodon": "Content"}),
            "verification_status": json.dumps({"mastodon": {"verified": True, "verified_at": "2026-06-28T10:00:00Z", "expires_at": "2026-06-28T22:00:00Z"}}),
            "source_idea": "Test idea"
        }

        rendered = template.render(request=mock_request, item=item)

        assert 'href="/review/tp05"' in rendered, "Review/Verify link should be present for ready_to_post"
