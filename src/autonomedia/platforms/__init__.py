"""Platform-specific handlers for posting content."""

# Lazy imports to avoid circular dependencies
def get_linkedin_handler():
    from autonomedia.platforms.linkedin.task_handler import LinkedInHandler
    return LinkedInHandler

def get_x_handler():
    from autonomedia.platforms.x.task_handler import XHandler
    return XHandler

__all__ = ["get_linkedin_handler", "get_x_handler"]
