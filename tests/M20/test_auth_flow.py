#!/usr/bin/env python3
# {Verification IDs: VER-M20S2-007}
# {Requirement IDs: FR-AUTH_FLOW}
# Test Type: INTEGRATION_TEST

import asyncio
import json
import os
import pytest
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Import the auth flow components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.reauth.reauth_script import (
    AuthTokenManager,
    ReauthLogger,
    ReauthManager,
)


class TestAuthFlow:
    """Test suite for the authentication flow and reauthentication operations."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_token_file = os.path.join(self.temp_dir, "test_tokens.json")
        
        # Create test tokens data
        self.test_tokens = {
            "linkedin": {
                "access_token": "test_linked_in_token",
                "refresh_token": "test_refresh_token",
                "expires_at": "2026-08-26T15:00:00Z"
            },
            "x": {
                "access_token": "test_x_token",
                "refresh_token": "test_x_refresh_token",
                "expires_at": "2026-08-26T15:00:00Z"
            },
            "mastodon": {
                "access_token": "test_mastodon_token",
                "refresh_token": "test_mastodon_refresh_token",
                "expires_at": "2026-08-26T15:00:00Z"
            }
        }
        
        # Write test tokens to file
        with open(self.test_token_file, "w") as f:
            json.dump(self.test_tokens, f)

    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_token_manager_initialization(self):
        """Test that AuthTokenManager initializes correctly."""
        token_manager = AuthTokenManager()
        
        # Test default paths
        assert token_manager.token_path == "./.env/.tokens.json"
        assert token_manager.backup_path == "./.env/.tokens.json.backup"
        
        # Test logger initialization
        assert token_manager.logger is not None

    def test_token_manager_load_tokens_empty(self):
        """Test loading tokens from non-existent file returns empty dict."""
        token_manager = AuthTokenManager()
        
        # Override token path to non-existent file
        token_manager.token_path = "/tmp/nonexistent.json"
        
        result = token_manager.load_tokens()
        assert result == {}

    def test_token_manager_load_tokens_valid(self):
        """Test loading valid tokens from file."""
        token_manager = AuthTokenManager()
        
        # Override token path to test file
        token_manager.token_path = self.test_token_file
        
        result = token_manager.load_tokens()
        
        assert "linkedin" in result
        assert "x" in result
        assert "mastodon" in result
        assert result["linkedin"]["access_token"] == "test_linked_in_token"
        assert result["x"]["access_token"] == "test_x_token"
        assert result["mastodon"]["access_token"] == "test_mastodon_token"

    def test_token_manager_save_tokens(self):
        """Test saving tokens to file."""
        token_manager = AuthTokenManager()
        
        # Save test tokens
        token_manager.save_tokens(self.test_token_file, self.test_tokens)
        
        # Load and verify
        result = token_manager.load_tokens()
        assert result == self.test_tokens

    def test_token_manager_get_token_valid(self):
        """Test retrieving a valid token for a platform."""
        token_manager = AuthTokenManager()
        
        # Override token path
        token_manager.token_path = self.test_token_file
        
        token_data = token_manager.get_token("linkedin", self.test_token_file)
        
        assert token_data is not None
        assert token_data["access_token"] == "test_linked_in_token"
        assert token_data["refresh_token"] == "test_refresh_token"

    def test_token_manager_get_token_invalid_platform(self):
        """Test retrieving token for non-existent platform returns None."""
        token_manager = AuthTokenManager()
        
        # Override token path
        token_manager.token_path = self.test_token_file
        
        token_data = token_manager.get_token("invalid_platform", self.test_token_file)
        
        assert token_data is None

    def test_token_manager_is_token_expired_valid(self):
        """Test checking if a valid token is expired (should return False)."""
        token_manager = AuthTokenManager()
        
        token_data = {
            "access_token": "test_token",
            "expires_at": "2026-08-26T15:00:00Z"
        }
        
        # Mock datetime to return a time before expiration
        with patch("scripts.reauth.reauth_script.datetime") as mock_datetime:
            mock_datetime.now.return_value = MagicMock(
                isoformat=lambda: "2026-08-26T14:00:00Z"
            )
            mock_datetime.fromisoformat.return_value = MagicMock(
                timestamp=lambda: 1685376000  # 2026-08-26 14:00:00 UTC
            )
            
            result = token_manager.is_token_expired(token_data)
            assert result is False

    def test_token_manager_is_token_expired_expired(self):
        """Test checking if an expired token is detected (should return True)."""
        token_manager = AuthTokenManager()
        
        token_data = {
            "access_token": "test_token",
            "expires_at": "2026-08-26T15:00:00Z"
        }
        
        # Mock datetime to return a time after expiration
        with patch("scripts.reauth.reauth_script.datetime") as mock_datetime:
            mock_datetime.now.return_value = MagicMock(
                isoformat=lambda: "2026-08-26T16:00:00Z"
            )
            mock_datetime.fromisoformat.return_value = MagicMock(
                timestamp=lambda: 1685379600  # 2026-08-26 16:00:00 UTC
            )
            
            result = token_manager.is_token_expired(token_data)
            assert result is True

    def test_reauth_logger_log_info(self):
        """Test logging info level messages."""
        logger = ReauthLogger()
        
        # Mock the logger to capture calls
        with patch.object(logger, "_log") as mock_log:
            logger.log_info("Test info message", {"platform": "linkedin"})
            
            mock_log.assert_called_once_with("info", "Test info message", {"platform": "linkedin"})

    def test_reauth_logger_log_error(self):
        """Test logging error level messages."""
        logger = ReauthLogger()
        
        # Mock the logger to capture calls
        with patch.object(logger, "_log") as mock_log:
            logger.log_error("Test error message", {"error": "connection_failed"})
            
            mock_log.assert_called_once_with("error", "Test error message", {"error": "connection_failed"})

    def test_reauth_manager_initialization(self):
        """Test ReauthManager initialization."""
        token_manager = AuthTokenManager()
        logger = ReauthLogger()
        
        # Mock get_handler to avoid dependency issues
        with patch("scripts.reauth.reauth_script.get_handler") as mock_get_handler:
            mock_handler = MagicMock(spec=PlatformHandler)
            mock_get_handler.return_value = mock_handler
            
            manager = ReauthManager(token_manager, logger)
            
            assert manager.token_manager == token_manager
            assert manager.logger == logger
            assert manager.supported_platforms == ["linkedin", "x", "mastodon"]

    @pytest.mark.asyncio
    async def test_reauth_manager_reauthenticate_platform_success(self):
        """Test successful reauthentication for a platform."""
        token_manager = AuthTokenManager()
        logger = ReauthLogger()
        
        # Mock dependencies
        with patch("scripts.reauth.reauth_script.get_handler") as mock_get_handler, \
             patch.object(token_manager, "get_token") as mock_get_token, \
             patch.object(token_manager, "save_tokens") as mock_save_tokens, \
             patch("scripts.reauth.reauth_script.BrowserProvider") as mock_browser_provider:
            
            # Setup mocks
            mock_handler = MagicMock(spec=PlatformHandler)
            mock_get_handler.return_value = mock_handler
            
            mock_get_token.return_value = self.test_tokens["linkedin"]
            
            mock_browser_instance = MagicMock()
            mock_browser_instance.authenticate = AsyncMock(return_value="new_token")
            mock_browser_provider.return_value = mock_browser_instance
            
            # Create manager
            manager = ReauthManager(token_manager, logger)
            
            # Test reauthentication
            result = await manager.reauthenticate_platform("linkedin", self.test_token_file)
            
            # Verify calls
            mock_get_token.assert_called_once_with("linkedin", self.test_token_file)
            mock_browser_instance.authenticate.assert_called_once()
            mock_save_tokens.assert_called_once()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_reauth_manager_reauthenticate_platform_token_missing(self):
        """Test reauthentication when token is missing."""
        token_manager = AuthTokenManager()
        logger = ReauthLogger()
        
        # Mock get_handler
        with patch("scripts.reauth.reauth_script.get_handler") as mock_get_handler:
            mock_handler = MagicMock(spec=PlatformHandler)
            mock_get_handler.return_value = mock_handler
            
            # Mock get_token to return None (token not found)
            with patch.object(token_manager, "get_token", return_value=None):
                manager = ReauthManager(token_manager, logger)
                
                result = await manager.reauthenticate_platform("linkedin", self.test_token_file)
                
                assert result is False

    @pytest.mark.asyncio
    async def test_reauth_manager_reauthenticate_all_platforms_success(self):
        """Test successful reauthentication for all supported platforms."""
        token_manager = AuthTokenManager()
        logger = ReauthLogger()
        
        # Mock dependencies for all platforms
        with patch("scripts.reauth.reauth_script.get_handler") as mock_get_handler, \
             patch.object(token_manager, "get_token") as mock_get_token, \
             patch.object(token_manager, "save_tokens") as mock_save_tokens, \
             patch("scripts.reauth.reauth_script.BrowserProvider") as mock_browser_provider:
            
            # Setup mocks for all platforms
            mock_handler = MagicMock(spec=PlatformHandler)
            mock_get_handler.return_value = mock_handler
            
            mock_get_token.return_value = self.test_tokens["linkedin"]
            
            mock_browser_instance = MagicMock()
            mock_browser_instance.authenticate = AsyncMock(return_value="new_token")
            mock_browser_provider.return_value = mock_browser_instance
            
            # Create manager
            manager = ReauthManager(token_manager, logger)
            
            # Test reauthentication for all platforms
            result = await manager.reauthenticate_all_platforms(self.test_token_file)
            
            # Verify calls for each platform
            assert mock_get_token.call_count == 3  # linkedin, x, mastodon
            assert mock_browser_instance.authenticate.call_count == 3
            assert mock_save_tokens.call_count == 3
            
            assert result is True

    def test_token_manager_validate_token_data_valid(self):
        """Test validation of valid token data."""
        token_manager = AuthTokenManager()
        
        valid_token = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": "2026-08-26T15:00:00Z"
        }
        
        result = token_manager.validate_token_data(valid_token)
        assert result is True

    def test_token_manager_validate_token_data_invalid(self):
        """Test validation of invalid token data (missing required fields)."""
        token_manager = AuthTokenManager()
        
        invalid_token = {
            "access_token": "test_token"
            # Missing refresh_token and expires_at
        }
        
        result = token_manager.validate_token_data(invalid_token)
        assert result is False

    def test_token_manager_backup_tokens(self):
        """Test backing up tokens to backup file."""
        token_manager = AuthTokenManager()
        
        # Create source tokens file
        source_file = os.path.join(self.temp_dir, "source_tokens.json")
        with open(source_file, "w") as f:
            json.dump(self.test_tokens, f)
        
        # Backup the file
        result = token_manager.backup_tokens(source_file)
        
        # Verify backup was created
        backup_file = source_file + ".backup"
        assert os.path.exists(backup_file)
        
        # Load and verify backup contents
        with open(backup_file, "r") as f:
            backup_data = json.load(f)
        
        assert backup_data == self.test_tokens
        
        # Clean up
        os.remove(backup_file)

    def test_logger_initialization(self):
        """Test ReauthLogger initialization with default settings."""
        logger = ReauthLogger()
        
        assert logger.level == "info"
        assert logger.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert logger.logger is not None

    @pytest.mark.asyncio
    async def test_full_auth_flow_integration(self):
        """Test full authentication flow integration."""
        # This test simulates a complete auth flow
        token_manager = AuthTokenManager()
        logger = ReauthLogger()
        
        # Mock all external dependencies
        with patch("scripts.reauth.reauth_script.get_handler") as mock_get_handler, \
             patch("scripts.reauth.reauth_script.BrowserProvider") as mock_browser_provider:
            
            # Setup mocks
            mock_handler = MagicMock(spec=PlatformHandler)
            mock_get_handler.return_value = mock_handler
            
            mock_browser_instance = MagicMock()
            mock_browser_instance.authenticate = AsyncMock(return_value="authenticated_token")
            mock_browser_provider.return_value = mock_browser_instance
            
            # Create manager
            manager = ReauthManager(token_manager, logger)
            
            # Simulate loading existing tokens
            token_manager.save_tokens(self.test_token_file, self.test_tokens)
            
            # Reauthenticate each platform
            for platform in ["linkedin", "x", "mastodon"]:
                result = await manager.reauthenticate_platform(platform, self.test_token_file)
                assert result is True
            
            # Verify tokens were updated
            updated_tokens = token_manager.load_tokens()
            for platform in ["linkedin", "x", "mastodon"]:
                assert platform in updated_tokens
                assert updated_tokens[platform]["access_token"] == "authenticated_token"

    def test_error_handling_invalid_file_path(self):
        """Test error handling for invalid file paths."""
        token_manager = AuthTokenManager()
        
        # Test with invalid path
        result = token_manager.load_tokens()
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])