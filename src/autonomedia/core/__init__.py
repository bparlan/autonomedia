"""Core modules for autonomedia."""

from autonomedia.core.platform import (
    batch_post,
    get_handler,
    get_supported_platforms,
    normalize_content,
    post,
    post_to_linkedin,
    post_to_x,
    register_handler,
)

__all__ = [
    "post",
    "post_to_linkedin",
    "post_to_x",
    "batch_post",
    "normalize_content",
    "get_handler",
    "register_handler",
    "get_supported_platforms",
]
