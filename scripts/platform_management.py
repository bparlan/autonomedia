#!/usr/bin/env python3
"""
Platform management UI script for operator interaction.
Provides tabbed interface for platform status and reauthentication.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomedia.core.platform import get_handler, get_supported_platforms
from scripts.reauth.reauth_script import ReauthManager


async def display_platform_status(platform_name: str, browser_data_dir: str, task_id: str | None = None) -> dict[str, Any]:
    """Display authentication status for a specific platform.
    
    Args:
        platform_name: Name of the platform.
        browser_data_dir: Path to browser data directory.
        task_id: Optional task ID for tracking.
        
    Returns:
        Status dictionary with authentication and rate limit info.
    """
    handler = get_handler(platform_name, browser_data_dir, task_id=task_id)
    
    # Check auth status
    auth_valid = await handler.validate_auth()
    
    # Get rate limit status
    rate_info = await handler.get_rate_limit_status()
    
    return {
        "platform": platform_name,
        "status": "valid" if auth_valid else "invalid",
        "last_authenticated": "N/A",
        "expires_at": "N/A",
        "rate_limit": rate_info,
        "error": None if auth_valid else "Authentication required",
    }


async def display_all_platforms_status(platform_name: str | None = None, browser_data_dir: str | None = None) -> dict[str, Any]:
    """Display status for all platforms or a specific one.
    
    Args:
        platform_name: If provided, check only this platform.
        browser_data_dir: Path to browser data directory.
        
    Returns:
        Dictionary with status for each platform.
    """
    if browser_data_dir is None:
        browser_data_dir = os.getenv(
            "BROWSER_DATA_DIR",
            str(Path(__file__).parent.parent / "runtime" / "browser_profiles"),
        )
    
    results = {}
    
    platforms = [platform_name] if platform_name else get_supported_platforms()
    
    for platform in platforms:
        try:
            results[platform] = await display_platform_status(platform, browser_data_dir)
        except Exception as e:
            results[platform] = {
                "platform": platform,
                "status": "error",
                "last_authenticated": "N/A",
                "expires_at": "N/A",
                "rate_limit": {},
                "error": str(e),
            }
    
    return results


async def reauthenticate_platform(platform_name: str, browser_data_dir: str, dry_run: bool = False, task_id: str | None = None) -> dict[str, Any]:
    """Reauthenticate a specific platform.
    
    Args:
        platform_name: Name of the platform.
        browser_data_dir: Path to browser data directory.
        dry_run: If True, validate auth without posting.
        task_id: Optional task ID for tracking.
        
    Returns:
        Reauthentication result dictionary.
    """
    manager = ReauthManager(browser_data_dir=browser_data_dir, task_id=task_id)
    return await manager.reauth_platform(platform_name, dry_run=dry_run)


async def reauthenticate_all_platforms(platform_name: str | None = None, browser_data_dir: str | None = None, dry_run: bool = False, task_id: str | None = None) -> dict[str, Any]:
    """Reauthenticate all platforms or a specific one.
    
    Args:
        platform_name: If provided, reauth only this platform.
        browser_data_dir: Path to browser data directory.
        dry_run: If True, validate auth without posting.
        task_id: Optional task ID for tracking.
        
    Returns:
        Dictionary with reauth results.
    """
    if browser_data_dir is None:
        browser_data_dir = os.getenv(
            "BROWSER_DATA_DIR",
            str(Path(__file__).parent.parent / "runtime" / "browser_profiles"),
        )
    
    if platform_name:
        return {platform_name: await reauthenticate_platform(platform_name, browser_data_dir, dry_run, task_id)}
    
    manager = ReauthManager(browser_data_dir=browser_data_dir, task_id=task_id)
    return await manager.reauth_all(dry_run=dry_run)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Platform management UI for autonomedia.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check status of all platforms
  python scripts/platform_management.py status

  # Check status of specific platform
  python scripts/platform_management.py status linkedin

  # Reauthenticate all platforms
  python scripts/platform_management.py reauth

  # Reauthenticate specific platform
  python scripts/platform_management.py reauth linkedin

  # Check rate limits
  python scripts/platform_management.py rates

  # List all supported platforms
  python scripts/platform_management.py list
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check platform status")
    status_parser.add_argument("platform", nargs="?", help="Platform to check (all if not specified)")

    # Reauth command
    reauth_parser = subparsers.add_parser("reauth", help="Reauthenticate platforms")
    reauth_parser.add_argument("platform", nargs="?", help="Platform to reauth (all if not specified)")
    reauth_parser.add_argument("--dry-run", action="store_true", help="Validate auth without posting")

    # Rates command
    rates_parser = subparsers.add_parser("rates", help="Check rate limit status")
    rates_parser.add_argument("platform", nargs="?", help="Platform to check (all if not specified)")

    # List command
    list_parser = subparsers.add_parser("list", help="List supported platforms")

    # Common args
    parser.add_argument("--task-id", help="Task ID for tracking")

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    if not args.command:
        print("Error: No command specified. Use 'status', 'reauth', 'rates', or 'list'.")
        sys.exit(1)

    # Get browser data directory
    browser_data_dir = os.getenv(
        "BROWSER_DATA_DIR",
        str(Path(__file__).parent.parent / "runtime" / "browser_profiles"),
    )

    if args.command == "status":
        results = await display_all_platforms_status(args.platform, browser_data_dir)
        print(json.dumps(results, indent=2))

    elif args.command == "reauth":
        results = await reauthenticate_all_platforms(
            args.platform, browser_data_dir, 
            dry_run=getattr(args, "dry_run", False),
            task_id=getattr(args, "task_id", None)
        )
        print(json.dumps(results, indent=2))

    elif args.command == "rates":
        if args.platform:
            handler = get_handler(args.platform, browser_data_dir, task_id=args.task_id)
            results = {args.platform: await handler.get_rate_limit_status()}
        else:
            results = {}
            for platform in get_supported_platforms():
                handler = get_handler(platform, browser_data_dir, task_id=args.task_id)
                results[platform] = await handler.get_rate_limit_status()
        print(json.dumps(results, indent=2))

    elif args.command == "list":
        platforms = get_supported_platforms()
        print(json.dumps({"supported_platforms": platforms}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())