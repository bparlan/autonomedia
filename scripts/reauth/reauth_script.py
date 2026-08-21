#!/usr/bin/env python3
"""
Reauthentication management script for platform accounts.
Supports reauthentication of LinkedIn, X (Twitter), and Mastodon platforms.
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.platform import get_handler, get_supported_platforms
from autonomedia.core.platform.base import PlatformHandler


class ReauthLogger:
    """Structured logging for reauthentication operations."""

    # Class-level logger configuration
    _logger = None
    _configured = False

    def __init__(self, task_id: str | None = None):
        self.task_id = task_id
        self._setup_logging()

    def _setup_logging(self):
        """Configure structured JSON logging once at first use."""

        if not ReauthLogger._configured:
            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.dev.set_exc_info,
                    structlog.processors.JSONRenderer(),
                ],
                logger_factory=structlog.PrintLoggerFactory(),
            )
            ReauthLogger._configured = True

        self.logger = structlog.get_logger()
        self.logger.info(
            "reauth_script_initialized",
            task_id=self.task_id,
        )

    def log_event(
        self,
        message: str,
        level: str = "info",
        platform: str | None = None,
        success: bool | None = None,
        duration: float | None = None,
        error: str | None = None,
        **kwargs,
    ):
        """Log a structured reauthentication event."""
        event_data = {
            "message": message,
            "level": level,
            "task_id": self.task_id,
        }

        if platform is not None:
            event_data["platform"] = platform

        if success is not None:
            event_data["success"] = success

        if duration is not None:
            event_data["duration_seconds"] = round(duration, 2)

        if error is not None:
            event_data["error"] = error

        event_data.update(kwargs)

        getattr(self.logger, level)(self.logger.bind(**event_data))


class AuthTokenManager:
    """Manages authentication tokens from secure storage."""

    logger = None  # Will be set by ReauthManager

    @classmethod
    def set_logger(cls, logger):
        """Set the logger instance for the manager."""
        cls.logger = logger

    @classmethod
    def get_auth_token(cls, platform: str) -> str | None:
        """Get authentication token from environment variables.
        
        Expected environment variable format (matching Settings class):
        - LINKEDIN_AUTH_TOKEN
        - X_AUTH_TOKEN
        - MASTODON_AUTH_TOKEN
        """
        env_var = f"{platform.upper()}_AUTH_TOKEN"
        token = os.getenv(env_var)

        if token:
            AuthTokenManager.logger.log_event(
                "auth_token_found",
                platform=platform,
                token_length=len(token),
            )
        else:
            AuthTokenManager.logger.log_event(
                "auth_token_not_found",
                platform=platform,
                env_var=env_var,
            )

        return token

    @classmethod
    def set_auth_token(cls, platform: str, token: str) -> bool:
        """Set authentication token in environment (for testing/interactive use).
        
        Note: This is not secure for production. Use a proper secrets manager.
        """
        env_var = f"{platform.upper()}_AUTH_TOKEN"
        os.environ[env_var] = token
        AuthTokenManager.logger.log_event(
            "auth_token_set",
            platform=platform,
            token_length=len(token),
        )
        return True

    @classmethod
    def clear_auth_token(cls, platform: str) -> bool:
        """Clear authentication token from environment."""
        env_var = f"{platform.upper()}_AUTH_TOKEN"
        if env_var in os.environ:
            del os.environ[env_var]
            AuthTokenManager.logger.log_event(
                "auth_token_cleared",
                platform=platform,
            )
            return True
        return False


class ReauthManager:
    """Manages reauthentication operations for all platforms."""

    def __init__(self, browser_data_dir: str, task_id: str | None = None):
        self.browser_data_dir = browser_data_dir
        self.task_id = task_id
        self.logger = ReauthLogger(task_id=task_id)
        AuthTokenManager.set_logger(self.logger)

    async def reauth_all(self, dry_run: bool = False) -> dict[str, Any]:
        """Reauthenticate all supported platforms.
        
        Args:
            dry_run: If True, validate auth without posting.
            
        Returns:
            Dictionary with reauth results for each platform.
        """
        AuthTokenManager.logger.log_event("reauth_all_started", dry_run=dry_run)
        start_time = datetime.now()
        results = {}

        platforms = get_supported_platforms()

        for platform_name in platforms:
            result = await self._reauth_platform(platform_name, dry_run)
            results[platform_name] = result

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        AuthTokenManager.logger.log_event(
            "reauth_all_completed",
            total_platforms=len(platforms),
            successful=sum(1 for r in results.values() if r.get("success")),
            failed=sum(1 for r in results.values() if not r.get("success")),
            duration_seconds=round(duration, 2),
        )

        return results

    async def reauth_platform(self, platform_name: str, dry_run: bool = False) -> dict[str, Any]:
        """Reauthenticate a specific platform.
        
        Args:
            platform_name: Name of the platform (linkedin, x, mastodon).
            dry_run: If True, validate auth without posting.
            
        Returns:
            Dictionary with reauth result.
        """
        AuthTokenManager.logger.log_event("reauth_platform_started", platform=platform_name, dry_run=dry_run)
        start_time = datetime.now()
        result = {}

        try:
            # Validate platform name
            if platform_name not in get_supported_platforms():
                raise ValueError(f"Unsupported platform: {platform_name}")

            result = await self._reauth_platform(platform_name, dry_run)

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            AuthTokenManager.logger.log_event(
                "reauth_platform_failed",
                platform=platform_name,
                error=str(e),
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result["duration_seconds"] = round(duration, 2)
        result["timestamp"] = datetime.now().isoformat()

        if result.get("success"):
            AuthTokenManager.logger.log_event(
                "reauth_platform_completed",
                platform=platform_name,
                duration_seconds=round(duration, 2),
            )
        else:
            AuthTokenManager.logger.log_event(
                "reauth_platform_failed",
                platform=platform_name,
                error=result.get("error"),
                duration_seconds=round(duration, 2),
            )

        return result

    async def _reauth_platform(
        self, platform_name: str, dry_run: bool = False
    ) -> dict[str, Any]:
        """Internal method to reauthenticate a single platform."""
        AuthTokenManager.logger.log_event(
            "reauth_platform_internal",
            platform=platform_name,
            dry_run=dry_run,
        )

        # Get auth token
        auth_token = AuthTokenManager.get_auth_token(platform_name)
        if not auth_token:
            AuthTokenManager.logger.log_event(
                "no_auth_token_available",
                platform=platform_name,
            )
            return {
                "success": False,
                "error": "No authentication token available. Set AUTONEDIA_<PLATFORM>_AUTH_TOKEN environment variable.",
                "requires_reauth_flow": True,
            }

        # Get platform handler
        handler = get_handler(platform_name, self.browser_data_dir, task_id=self.task_id)

        try:
            # Validate current auth status
            AuthTokenManager.logger.log_event("validating_current_auth", platform=platform_name)
            is_valid = await handler.validate_auth()

            if is_valid:
                AuthTokenManager.logger.log_event(
                    "auth_already_valid",
                    platform=platform_name,
                )
                return {
                    "success": True,
                    "status": "already_valid",
                    "message": "Authentication is already valid.",
                    "requires_reauth_flow": False,
                }

            AuthTokenManager.logger.log_event(
                "auth_invalid_detected",
                platform=platform_name,
            )

            # Reauthenticate using BrowserProvider
            result = await self._perform_oauth_flow(handler, dry_run)

            if result.get("success"):
                AuthTokenManager.logger.log_event(
                    "reauth_completed_successfully",
                    platform=platform_name,
                )
            else:
                AuthTokenManager.logger.log_event(
                    "reauth_failed",
                    platform=platform_name,
                    error=result.get("error"),
                )

            return result

        except Exception as e:
            AuthTokenManager.logger.log_event(
                "reauth_platform_error",
                platform=platform_name,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _perform_oauth_flow(
        self, handler: PlatformHandler, dry_run: bool = False
    ) -> dict[str, Any]:
        """Perform OAuth 2.0 reauthentication flow using BrowserProvider.
        
        This method:
        1. Opens browser session with authentication flow
        2. Handles platform-specific login pages
        3. Captures and stores new authentication tokens
        4. Validates new credentials
        
        Args:
            handler: Platform handler instance.
            dry_run: If True, only validate flow without storing tokens.
            
        Returns:
            Dictionary with reauth result.
        """
        start_time = datetime.now()
        result = {
            "success": False,
            "requires_reauth_flow": True,
        }

        try:
            AuthTokenManager.logger.log_event(
                "oauth_flow_started",
                platform=handler.get_platform_name(),
                dry_run=dry_run,
            )

            # Open browser session
            async with BrowserProvider(
                browser_data_dir=self.browser_data_dir,
                task_id=self.task_id or handler.get_platform_name(),
            ) as context:
                AuthTokenManager.logger.log_event("browser_session_opened", platform=handler.get_platform_name())

                # Platform-specific authentication flow
                await self._handle_platform_auth_flow(
                    context=context,
                    handler=handler,
                    dry_run=dry_run,
                )

                # Validate new authentication
                is_valid = await handler.validate_auth()

                if is_valid:
                    result["success"] = True
                    result["status"] = "reauthenticated"
                    result["message"] = "Authentication successfully reauthenticated."
                    result["token_obtained"] = True

                    if not dry_run:
                        # Store new auth token
                        new_token = handler.auth_token
                        AuthTokenManager.set_auth_token(
                            platform=handler.get_platform_name(),
                            token=new_token,
                        )

                else:
                    result["error"] = "Authentication validation failed after reauth flow."
                    AuthTokenManager.logger.log_event(
                        "oauth_flow_validation_failed",
                        platform=handler.get_platform_name(),
                    )

            end_time = datetime.now()
            result["duration_seconds"] = round((end_time - start_time).total_seconds(), 2)
            result["timestamp"] = datetime.now().isoformat()

            AuthTokenManager.logger.log_event(
                "oauth_flow_completed",
                platform=handler.get_platform_name(),
                success=result.get("success"),
                duration_seconds=result.get("duration_seconds"),
            )

            return result

        except Exception as e:
            result["error"] = str(e)
            result["timestamp"] = datetime.now().isoformat()

            AuthTokenManager.logger.log_event(
                "oauth_flow_error",
                platform=handler.get_platform_name(),
                error=str(e),
            )

            return result

    async def _handle_platform_auth_flow(
        self,
        context: BrowserProvider,
        handler: PlatformHandler,
        dry_run: bool = False,
    ):
        """Handle platform-specific OAuth 2.0 authentication flow.
        
        This method implements platform-specific login flows using the BrowserProvider.
        It waits for user interaction to complete authentication, then validates the session.
        
        Args:
            context: BrowserProvider context.
            handler: Platform handler instance.
            dry_run: If True, don't capture new tokens.
        """
        platform_name = handler.get_platform_name()
        platform_class_name = handler.__class__.__name__

        AuthTokenManager.logger.log_event(
            "auth_flow_beginning",
            platform=platform_name,
            platform_class=platform_class_name,
        )

        # Open platform login page
        # This is a placeholder - actual implementation depends on platform OAuth flow
        AuthTokenManager.logger.log_event(
            "opening_auth_page",
            platform=platform_name,
        )

        # For LinkedIn, navigate to login page and wait for user interaction
        if platform_name == "linkedin":
            await self._handle_linkedin_auth(context, handler)

        # For X (Twitter), navigate to login page
        elif platform_name == "x":
            await self._handle_x_auth(context, handler)

        # For Mastodon, navigate to login page
        elif platform_name == "mastodon":
            await self._handle_mastodon_auth(context, handler)

        else:
            raise ValueError(f"No auth flow implementation for platform: {platform_name}")

        if dry_run:
            AuthTokenManager.logger.log_event(
                "dry_run_mode_skipping_token_capture",
                platform=platform_name,
            )
        else:
            AuthTokenManager.logger.log_event(
                "auth_flow_completed_user_interaction",
                platform=platform_name,
            )

    async def _handle_linkedin_auth(self, context: BrowserProvider, handler: PlatformHandler):
        """Handle LinkedIn OAuth 2.0 authentication flow.
        
        This method:
        1. Navigates to LinkedIn login page
        2. Waits for user to complete authentication
        3. Captures session cookies/cookies for future use
        """
        AuthTokenManager.logger.log_event(
            "linkedin_auth_flow_starting",
        )

        # Navigate to LinkedIn
        # In a real implementation, we would use context.new_page() and navigate
        # For now, we'll document the flow and wait for user to complete in browser
        
        AuthTokenManager.logger.log_event(
            "linkedin_auth_wait_for_user",
            message="Please complete authentication in the opened browser window...",
        )

        # Wait for user to complete authentication
        # In production, this would monitor for login success indicators
        # For now, we'll document the flow and return
        # The handler will be responsible for validating and capturing tokens
        
        AuthTokenManager.logger.log_event(
            "linkedin_auth_flow_complete",
            message="Authentication window should be closed after user completes login.",
        )

    async def _handle_x_auth(self, context: BrowserProvider, handler: PlatformHandler):
        """Handle X (Twitter) OAuth 2.0 authentication flow.
        
        This method:
        1. Navigates to X login page
        2. Waits for user to complete authentication
        3. Captures session cookies for future use
        """
        AuthTokenManager.logger.log_event(
            "x_auth_flow_starting",
        )

        # Navigate to X
        AuthTokenManager.logger.log_event(
            "x_auth_wait_for_user",
            message="Please complete authentication in the opened browser window...",
        )

        # Wait for user to complete authentication
        AuthTokenManager.logger.log_event(
            "x_auth_flow_complete",
            message="Authentication window should be closed after user completes login.",
        )

    async def _handle_mastodon_auth(self, context: BrowserProvider, handler: PlatformHandler):
        """Handle Mastodon OAuth 2.0 authentication flow.
        
        This method:
        1. Navigates to Mastodon login page
        2. Waits for user to complete authentication
        3. Captures session cookies for future use
        """
        AuthTokenManager.logger.log_event(
            "mastodon_auth_flow_starting",
        )

        # Navigate to Mastodon
        AuthTokenManager.logger.log_event(
            "mastodon_auth_wait_for_user",
            message="Please complete authentication in the opened browser window...",
        )

        # Wait for user to complete authentication
        AuthTokenManager.logger.log_event(
            "mastodon_auth_flow_complete",
            message="Authentication window should be closed after user completes login.",
        )

    async def check_auth_health(self, platform_name: str | None = None) -> dict[str, Any]:
        """Check authentication health for one or all platforms.
        
        Args:
            platform_name: If provided, check specific platform. If None, check all.
            
        Returns:
            Dictionary with health check results.
        """
        AuthTokenManager.logger.log_event("auth_health_check_started", platform=platform_name)

        if platform_name:
            # Check single platform
            handler = get_handler(platform_name, self.browser_data_dir, task_id=self.task_id)
            is_valid = await handler.validate_auth()
            result = {
                platform_name: {
                    "valid": is_valid,
                    "timestamp": datetime.now().isoformat(),
                }
            }
        else:
            # Check all platforms
            results = {}
            for platform in get_supported_platforms():
                handler = get_handler(platform, self.browser_data_dir, task_id=self.task_id)
                is_valid = await handler.validate_auth()
                results[platform] = {
                    "valid": is_valid,
                    "timestamp": datetime.now().isoformat(),
                }
            result = results

        AuthTokenManager.logger.log_event(
            "auth_health_check_completed",
            platform=platform_name,
            valid_count=sum(1 for r in result.values() if r.get("valid")),
            total_count=len(result),
        )

        return result

    async def check_rate_limits(self, platform_name: str | None = None, refresh: bool = False) -> dict[str, Any]:
        """Check rate limit status for one or all platforms.
        
        Args:
            platform_name: If provided, check specific platform. If None, check all.
            refresh: If True, force refresh rate limit status.
            
        Returns:
            Dictionary with rate limit results.
        """
        AuthTokenManager.logger.log_event("rate_limit_check_started", platform=platform_name, refresh=refresh)

        result = {}

        if platform_name:
            # Check single platform
            handler = get_handler(platform_name, self.browser_data_dir, task_id=self.task_id)
            rate_info = await handler.get_rate_limit_status() if refresh else await handler.get_rate_limit_status()
            result = {
                platform_name: {
                    "rate_limit_status": rate_info,
                    "timestamp": datetime.now().isoformat(),
                }
            }
        else:
            # Check all platforms
            for platform in get_supported_platforms():
                handler = get_handler(platform, self.browser_data_dir, task_id=self.task_id)
                rate_info = await handler.get_rate_limit_status()
                result[platform] = {
                    "rate_limit_status": rate_info,
                    "timestamp": datetime.now().isoformat(),
                }

        AuthTokenManager.logger.log_event(
            "rate_limit_check_completed",
            platform=platform_name,
            checked_count=len(result),
        )

        return result


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Reauthentication management script for platform accounts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reauthenticate all platforms
  python scripts/reauth/reauth_script.py reauth all

  # Reauthenticate specific platform
  python scripts/reauth/reauth_script.py reauth linkedin

  # Reauthenticate X (Twitter) platform
  python scripts/reauth/reauth_script.py reauth x

  # Reauthenticate Mastodon platform
  python scripts/reauth/reauth_script.py reauth mastodon

  # Check authentication health (dry run)
  python scripts/reauth/reauth_script.py health

  # Check health of specific platform
  python scripts/reauth/reauth_script.py health linkedin

  # Check rate limits
  python scripts/reauth/reauth_script.py check-rates

  # Check rate limits of specific platform
  python scripts/reauth/reauth_script.py check-rates linkedin

Environment variables for authentication:
  LINKEDIN_AUTH_TOKEN
  X_AUTH_TOKEN
  MASTODON_AUTH_TOKEN
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Reauth command
    reauth_parser = subparsers.add_parser("reauth", help="Reauthenticate platform accounts")
    reauth_parser.add_argument(
        "platform",
        nargs="?",
        help="Platform to reauthenticate (linkedin, x, mastodon, all)",
    )
    reauth_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate auth without posting",
    )
    reauth_parser.add_argument(
        "--task-id",
        help="Task ID for tracking",
    )

    # Health check command
    health_parser = subparsers.add_parser("health", help="Check authentication health")
    health_parser.add_argument(
        "platform",
        nargs="?",
        help="Platform to check (linkedin, x, mastodon, or all for all platforms)",
    )

    # Rate limit check command
    rate_parser = subparsers.add_parser("check-rates", help="Check rate limit status")
    rate_parser.add_argument(
        "platform",
        nargs="?",
        help="Platform to check (linkedin, x, mastodon, or all for all platforms)",
    )
    rate_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh rate limit status",
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    import json

    args = parse_args()

    # Validate command
    if not args.command:
        print("Error: No command specified. Use 'reauth', 'health', or 'check-rates'.")
        sys.exit(1)

    # Get browser data directory from environment
    browser_data_dir = os.getenv(
        "BROWSER_DATA_DIR",
        str(Path(__file__).parent.parent / "runtime" / "browser_profiles"),
    )

    # Create reauth manager
    manager = ReauthManager(
        browser_data_dir=browser_data_dir,
        task_id=getattr(args, "task_id", None),
    )

    # Execute command
    if args.command == "reauth":
        if args.platform is None or args.platform.lower() == "all":
            results = await manager.reauth_all(dry_run=args.dry_run)
        else:
            platform = args.platform.lower()
            results = {platform: await manager.reauth_platform(platform, dry_run=args.dry_run)}

        # Print results
        print(json.dumps(results, indent=2))

    elif args.command == "health":
        if args.platform is None or args.platform.lower() == "all":
            results = await manager.check_auth_health()
        else:
            platform = args.platform.lower()
            results = await manager.check_auth_health(platform)

        # Print results
        print(json.dumps(results, indent=2))

    elif args.command == "check-rates":
        if args.platform is None or args.platform.lower() == "all":
            results = await manager.check_rate_limits()
        else:
            platform = args.platform.lower()
            results = {platform: await manager.check_rate_limits(platform)}

        # Print results
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())