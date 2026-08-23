# Platform Abstraction Layer

## Overview

A unified platform abstraction layer for posting content to multiple social media platforms while maintaining Open/Closed Principle and anti-detection techniques.

## Architecture

### Base Class (`src/autonomedia/core/platform/base.py`)

Abstract base class `PlatformHandler` providing:

- **Abstract Methods**:
  - `post(content, options)` - Platform-specific posting
  - `validate_auth()` - Authentication validation

- **Common Behavior**:
  - Logging with timestamps and task IDs
  - Error handling and structured logging
  - Retry logic with exponential backoff (max 3 attempts)
  - Randomized delays for anti-detection
  - Content normalization (markdown stripping, whitespace normalization)
  - Randomized viewport sizes for browser automation

- **Configuration**:
  - Platform-specific character limits
  - Field limits (title, summary, hashtags, etc.)

### Platform Handlers

#### LinkedIn (`src/autonomedia/platforms/linkedin/task_handler.py`)

Features:
- **Title Extraction**: First 200 chars (max 300), no trailing period
- **Summary Extraction**: Remaining content (max 3000)
- **Tag Extraction**: Max 5 tags, 25 chars each, uppercase format (#TAG), no duplicates
- **Article Link**: Included in all posts
- **Formatting**: Professional tone, no trailing period on title
- **Anti-Detection**: Randomized delays (0.5-2.5s), randomized viewports

#### X (Twitter) (`src/autonomedia/platforms/x/task_handler.py`)

Features:
- **280-Character Limit**: Truncation with ellipsis
- **Hashtag Formatting**: #Hashtag camelCase, max 3 tags, no duplicates
- **Hook Preservation**: First line as strong hook
- **Article Link**: Preserved at end of tweet
- **Randomized Delays**: 5-10 seconds between posts
- **Batch Posting**: Support for posting multiple tweets sequentially
- **Anti-Detection**: Randomized delays, randomized viewports

#### Mastodon (Existing Handler)

- Already inherits from `PlatformHandler`
- Compatible with the abstraction layer
- Uses same pattern for posting

### Unified Abstraction Layer (`src/autonomedia/core/platform/__init__.py`)

Main entry point with:

- **Routing Function**: `post(content, options) -> dict`
  - Normalizes content
  - Routes to correct platform handler
  - Validates authentication
  - Handles retries and errors
  - Returns structured result

- **Content Normalization**: `normalize_content(content, options)`
  - Strips markdown formatting
  - Normalizes whitespace
  - Extracts title and summary
  - Platform-specific adjustments

- **Helper Functions**:
  - `post_to_linkedin(content, options)` - Convenience function
  - `post_to_x(content, options)` - Convenience function
  - `batch_post(contents, options)` - Batch posting to same platform
  - `get_handler(platform_name, browser_data_dir, task_id)` - Get handler instance
  - `register_handler(platform_name, handler_class)` - Register new platforms
  - `get_supported_platforms()` - Get list of supported platforms

## Usage

### Basic Usage

```python
from autonomedia.core.platform import post

# Post to LinkedIn
result = await post(
    content="Your content here...",
    options={
        "platform": "linkedin",
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
        "article_link": "https://example.com/article",
    }
)

# Post to X (Twitter)
result = await post(
    content="Your content here...",
    options={
        "platform": "x",
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
    }
)
```

### Using Convenience Functions

```python
from autonomedia.core.platform import post_to_linkedin, post_to_x

# LinkedIn
result = await post_to_linkedin(
    content="Your content here...",
    options={
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
    }
)

# X (Twitter)
result = await post_to_x(
    content="Your content here...",
    options={
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
        "batch_mode": True,
    }
)
```

### Batch Posting

```python
from autonomedia.core.platform import batch_post

# Post multiple tweets
results = await batch_post(
    contents=[
        "Tweet 1 content...",
        "Tweet 2 content...",
        "Tweet 3 content...",
    ],
    options={
        "platform": "x",
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
    }
)
```

## Authentication

Authentication is not yet implemented (TODO). Platforms require:
- OAuth 2.0 token
- API token
- Or session cookies

Tokens should be retrieved from:
- Environment variables
- Secure storage
- Configuration files

## Anti-Detection Techniques

1. **Randomized Delays**:
   - Human-like delays between actions
   - Jitter added to exponential backoff

2. **Randomized Viewports**:
   - Different viewport sizes simulate different devices
   - LinkedIn: 1280x800, 1366x768, 1536x864
   - X: Same range

3. **Human-like Behavior**:
   - Wait times between operations
   - Session health checks before posting
   - Patient UI interaction

## Error Handling

- **Retry Logic**: Exponential backoff with max 3 attempts
- **Error Logging**: Structured logging with timestamps and task IDs
- **Validation**: Content validation and authentication checks
- **Structured Results**: Clear status codes and error messages

## Extending to New Platforms

1. Create handler class inheriting from `PlatformHandler`
2. Implement abstract methods: `post()` and `validate_auth()`
3. Add platform-specific constants and formatting logic
4. Register handler in `core/platform/__init__.py`:

```python
from autonomedia.platforms.mastodon.task_handler import MastodonHandler

register_handler("mastodon", MastodonHandler)
```

5. Use via unified API:

```python
result = await post(
    content="Your content here...",
    options={
        "platform": "mastodon",
        "browser_data_dir": "./runtime/browser_profiles",
        "task_id": "task_123",
    }
)
```

## Files

### Core
- `src/autonomedia/core/platform/__init__.py` - Unified abstraction layer
- `src/autonomedia/core/platform/base.py` - Abstract base class

### Platforms
- `src/autonomedia/platforms/linkedin/task_handler.py` - LinkedIn handler
- `src/autonomedia/platforms/x/task_handler.py` - X (Twitter) handler
- `src/autonomedia/platforms/mastodon/task_handler.py` - Mastodon handler (existing)

### Modules
- `src/autonomedia/core/__init__.py` - Exports platform functions
- `src/autonomedia/platforms/__init__.py` - Platform handler exports

### Settings
- `src/autonomedia/core/config/settings.py` - Added LINKEDIN_URL and X_URL

## Testing

Run logic tests to verify implementation:

```bash
python test_platform_logic.py
```

Tests cover:
- Handler class structure
- LinkedIn handler components
- X handler components
- Unified abstraction layer
- Content normalization logic
- Tag/hashtag extraction and formatting
- Retry logic structure

## Compatibility

- **Open/Closed Principle**: New platforms can be added without modifying existing handlers
- **Existing Mastodon Handler**: Already inherits from PlatformHandler, remains compatible
- **No Hardcoded Tokens**: Authentication requires configuration
- **Structured Logging**: All operations logged with metadata

## Future Enhancements

1. OAuth 2.0 implementation for all platforms
2. Authentication token management in secure storage
3. Rate limiting and quota management
4. Content scheduling and queuing
5. Platform-specific content optimization
6. Analytics and posting metrics
