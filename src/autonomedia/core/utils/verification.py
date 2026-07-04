# Verification status parsing utilities (shared across M12/M13/M14)

import json
from typing import Any


def parse_verification_status(value: Any) -> dict:
    """
    Parse verification_status from DB string to dict.

    Handles both string (from DB) and dict formats gracefully.
    Returns empty dict on any error.

    Args:
        value: Raw verification_status value (string or dict)

    Returns:
        Parsed dict with platform keys, or empty dict
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            result = json.loads(value)
            return result if isinstance(result, dict) else {}
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def get_platform_verification(verification_status: dict, platform: str) -> dict:
    """
    Get platform-specific verification data with safe defaults.

    Args:
        verification_status: Parsed verification_status dict
        platform: Platform name (e.g., 'mastodon')

    Returns:
        Dict with 'verified', 'verified_at', 'expires_at' keys (defaults applied)
    """
    platform_status = verification_status.get(platform, {})
    if isinstance(platform_status, dict):
        return {
            "verified": platform_status.get("verified", False),
            "verified_at": platform_status.get("verified_at"),
            "expires_at": platform_status.get("expires_at"),
        }
    return {"verified": False, "verified_at": None, "expires_at": None}


def is_platform_verified(verification_status: dict, platform: str) -> bool:
    """
    Check if a platform is verified.

    Args:
        verification_status: Parsed verification_status dict
        platform: Platform name (e.g., 'mastodon')

    Returns:
        True if platform exists and is verified, False otherwise
    """
    data = get_platform_verification(verification_status, platform)
    return data.get("verified", False)


def get_verified_at_timestamp(verification_status: dict, platform: str) -> str:
    """
    Get verified_at timestamp for a platform (for sorting).

    Args:
        verification_status: Parsed verification_status dict
        platform: Platform name (e.g., 'mastodon')

    Returns:
        verified_at timestamp string, or empty string if not found
    """
    data = get_platform_verification(verification_status, platform)
    return data.get("verified_at", "")
