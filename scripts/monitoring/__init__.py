#!/usr/bin/env python3
"""
Monitoring utilities for platform operations.
Provides metrics collection and alerting functionality.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

# Platform rate limit constants
PLATFORM_RATE_LIMITS = {
    "linkedin": {"limit": 100, "window_seconds": 3600, "remaining_header": "X-RateLimit-Remaining"},
    "x": {"limit": 300, "window_seconds": 10800, "remaining_header": "x-rate-limit-remaining"},
    "mastodon": {"limit": None, "window_seconds": None, "remaining_header": None},
}


def calculate_success_rate(total: int, success: int) -> float:
    """Calculate success rate percentage.
    
    Args:
        total: Total number of operations.
        success: Number of successful operations.
        
    Returns:
        Success rate as percentage (0-100).
    """
    if total == 0:
        return 0.0
    return round((success / total) * 100, 2)


def get_rate_limit_utilization(platform: str, remaining: int) -> float:
    """Get rate limit utilization percentage.
    
    Args:
        platform: Platform name.
        remaining: Remaining requests.
        
    Returns:
        Utilization percentage (0-100).
    """
    limits = PLATFORM_RATE_LIMITS.get(platform, {})
    limit = limits.get("limit")
    
    if limit is None:
        return 0.0
    
    return round(((limit - remaining) / limit) * 100, 2)


def should_alert(success_rate: float, threshold: float = 80.0) -> bool:
    """Check if alert should be triggered for low success rate.
    
    Args:
        success_rate: Current success rate.
        threshold: Alert threshold (default 80%).
        
    Returns:
        True if alert should be triggered.
    """
    return success_rate < threshold


def should_alert_rate_limit(platform: str, remaining: int, threshold: float = 80.0) -> bool:
    """Check if rate limit alert should be triggered.
    
    Args:
        platform: Platform name.
        remaining: Remaining requests.
        threshold: Alert threshold percentage (default 80%).
        
    Returns:
        True if alert should be triggered.
    """
    utilization = get_rate_limit_utilization(platform, remaining)
    return utilization > threshold


def format_alert(platform: str, alert_type: str, message: str, severity: str = "warning") -> dict[str, Any]:
    """Format an alert message.
    
    Args:
        platform: Platform name.
        alert_type: Type of alert.
        message: Alert message.
        severity: Alert severity (info, warning, critical).
        
    Returns:
        Formatted alert dictionary.
    """
    return {
        "id": f"{platform}-{alert_type}-{datetime.now().isoformat()}",
        "platform": platform,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "resolved": False,
    }


def get_platform_constraints(platform: str) -> dict[str, Any]:
    """Get platform-specific constraints for publishing.
    
    Args:
        platform: Platform name.
        
    Returns:
        Dictionary with platform constraints.
    """
    return {
        "linkedin": {
            "max_length": 3000,
            "min_length": 200,
            "rate_limit": 100,
            "rate_window_seconds": 3600,
            "requires_media": False,
            "supports_threads": True,
            "supports_hashtags": True,
            "best_times": ["09:00-10:00", "12:00-13:00", "17:00-18:00"],
        },
        "x": {
            "max_length": 280,
            "min_length": 10,
            "rate_limit": 300,
            "rate_window_seconds": 10800,
            "requires_media": False,
            "supports_threads": True,
            "supports_hashtags": True,
            "best_times": ["08:00-10:00", "12:00-13:00", "18:00-20:00"],
        },
        "mastodon": {
            "max_length": 500,
            "min_length": 1,
            "rate_limit": None,
            "rate_window_seconds": None,
            "requires_media": False,
            "supports_threads": True,
            "supports_hashtags": True,
            "best_times": ["10:00-12:00", "14:00-16:00", "20:00-22:00"],
        },
    }.get(platform, {})


def adapt_content_for_platform(content: str, platform: str) -> str:
    """Adapt content for a specific platform.
    
    Args:
        content: Original content.
        platform: Target platform.
        
    Returns:
        Adapted content within platform constraints.
    """
    constraints = get_platform_constraints(platform)
    max_len = constraints.get("max_length", 280)
    
    if len(content) <= max_len:
        return content
    
    # Truncate to max length
    return content[:max_len-3] + "..."