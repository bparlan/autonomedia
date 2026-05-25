class ModerationError(Exception):
    pass

class ModerationAdapter:
    """
    Validates content against platform-specific rules before allowing it to proceed.
    Ensures that AI outputs do not violate hard limits (e.g. character counts) 
    and checks for fundamental safety.
    """
    
    PLATFORM_LIMITS = {
        "mastodon": {"max_chars": 500},
        "x": {"max_chars": 280},
        "linkedin": {"max_chars": 3000},
    }

    @classmethod
    def validate(cls, platform: str, content: str) -> bool:
        if not content:
            raise ModerationError("Content cannot be empty.")
        
        limits = cls.PLATFORM_LIMITS.get(platform)
        if limits:
            if len(content) > limits["max_chars"]:
                raise ModerationError(f"Content length {len(content)} exceeds {platform} limit of {limits['max_chars']}")
        
        # In the future: Add keyword blocks, spam-detection, or LLM-based safety checks here
        return True
