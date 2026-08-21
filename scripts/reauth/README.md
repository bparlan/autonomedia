# Reauthentication Script

A command-line tool for managing and reauthenticating platform accounts in the Autonomedia system.

## Overview

The reauthentication script provides a unified interface for managing authentication across multiple social media platforms. It supports:
- **LinkedIn** - Professional networking platform
- **X (Twitter)** - Microblogging platform
- **Mastodon** - Decentralized social network

## Features

- **Platform-specific reauthentication flows** using BrowserProvider for OAuth 2.0
- **Authentication health checking** with session validation
- **Dry-run mode** for testing without storing credentials
- **Structured JSON logging** with timestamps
- **Environment variable-based token storage** (extendable to secure vaults)
- **Support for task tracking** with optional task IDs

## Installation

No additional installation required. The script uses existing dependencies:
- `autonomedia.browser.provider` - Browser automation
- `autonomedia.core.platform` - Platform abstraction layer

## Usage

### Basic Commands

```bash
# Show help
python scripts/reauth/reauth_script.py --help

# Reauthenticate all platforms
python scripts/reauth/reauth_script.py reauth all

# Reauthenticate specific platform
python scripts/reauth/reauth_script.py reauth linkedin

# Reauthenticate X (Twitter)
python scripts/reauth/reauth_script.py reauth x

# Reauthenticate Mastodon
python scripts/reauth/reauth_script.py reauth mastodon
```

### Advanced Options

```bash
# Reauthenticate with dry-run mode (validate only, don't store tokens)
python scripts/reauth/reauth_script.py reauth linkedin --dry-run

# Reauthenticate with custom task ID
python scripts/reauth/reauth_script.py reauth x --task-id "daily-post-2026-07-08"

# Check authentication health for all platforms
python scripts/reauth/reauth_script.py health

# Check health of specific platform
python scripts/reauth/reauth_script.py health linkedin
```

### Authentication Tokens

Authentication tokens are stored in environment variables:

```bash
# Set authentication token for LinkedIn
export AUTONEDIA_LINKEDIN_AUTH_TOKEN="your_linkedin_token_here"

# Set authentication token for X (Twitter)
export AUTONEDIA_X_AUTH_TOKEN="your_x_token_here"

# Set authentication token for Mastodon
export AUTONEDIA_MASTODON_AUTH_TOKEN="your_mastodon_token_here"
```

**Note:** For production use, consider using a secure secrets manager (Vault, AWS Secrets Manager, etc.) instead of environment variables.

## Authentication Flow

### 1. Health Check

First, check if authentication is valid:

```bash
python scripts/reauth/reauth_script.py health linkedin
```

Example output:
```json
{
  "linkedin": {
    "valid": true,
    "timestamp": "2026-07-08T21:41:12.082966"
  }
}
```

### 2. Reauthentication

If authentication is invalid, trigger a reauthentication flow:

```bash
python scripts/reauth/reauth_script.py reauth linkedin
```

**What happens during reauthentication:**
1. Script validates current auth status
2. Opens browser session via BrowserProvider
3. Waits for user to complete authentication in browser
4. Validates new credentials
5. Stores new auth token (if not in dry-run mode)

### 3. Dry-Run Mode

Use dry-run mode to test the flow without storing credentials:

```bash
python scripts/reauth/reauth_script.py reauth linkedin --dry-run
```

## Platform-Specific Notes

### LinkedIn

- Uses professional profile credentials
- Requires OAuth 2.0 authorization
- Handles profile post formatting automatically
- Character limit: 30,000 characters

### X (Twitter)

- Uses API token or OAuth 2.0
- Handles tweet truncation automatically
- Character limit: 280 characters (base), 1000 for threads
- Includes hashtag extraction and formatting

### Mastodon

- Uses OAuth 2.0
- Handles toot formatting automatically
- Character limit: 500 characters
- Supports hashtags and mentions

## Environment Variables

| Variable | Platform | Description |
|----------|----------|-------------|
| `AUTONEDIA_LINKEDIN_AUTH_TOKEN` | LinkedIn | OAuth 2.0 access token |
| `AUTONEDIA_X_AUTH_TOKEN` | X (Twitter) | API token or OAuth token |
| `AUTONEDIA_MASTODON_AUTH_TOKEN` | Mastodon | OAuth 2.0 access token |
| `BROWSER_DATA_DIR` | All | Browser profile directory path |

## Logging

All operations are logged with structured JSON output:

```bash
python scripts/reauth/reauth_script.py reauth linkedin 2>&1 | jq .
```

Example log entries:
- `reauth_script_initialized` - Script startup
- `auth_health_check_started` - Health check initiation
- `auth_flow_beginning` - Authentication flow start
- `oauth_flow_started` - OAuth flow initiation
- `auth_platform_completed` - Successful reauthentication
- `auth_platform_failed` - Reauthentication failure

## Error Handling

The script handles various error scenarios:

- **Invalid platform name**: Returns error message with supported platforms
- **Missing authentication token**: Returns error with environment variable instructions
- **Authentication validation failed**: Returns error with details
- **Browser session errors**: Captures failure artifacts and logs errors

## Security Considerations

1. **Token Storage**: Currently uses environment variables (not secure for production)
2. **Token Exposure**: Avoid logging tokens or including them in output
3. **Browser Profiles**: Use separate browser profiles per platform for isolation
4. **HTTPS**: Always use HTTPS for authentication flows

## Future Enhancements

- [ ] Integration with AWS Secrets Manager / HashiCorp Vault
- [ ] Support for refresh token flow
- [ ] Automatic token rotation
- [ ] Integration with CI/CD pipelines
- [ ] Email notifications for failed reauth attempts
- [ ] Integration with SSO providers

## Troubleshooting

### No authentication token available

**Error**: `No authentication token available. Set AUTONEDIA_<PLATFORM>_AUTH_TOKEN environment variable.`

**Solution**: Set the appropriate environment variable for the platform.

### Browser session timeout

**Error**: Browser session timeout during reauthentication

**Solution**: Ensure browser profile directory is accessible and has sufficient disk space.

### Authentication validation failed

**Error**: `Authentication validation failed after reauth flow.`

**Solution**: 
1. Complete authentication in the browser
2. Ensure the handler correctly captures session cookies
3. Check browser logs for additional errors

## Development

### Adding New Platform Support

1. Create a new platform handler in `src/autonomedia/platforms/<platform>/task_handler.py`
2. Implement `validate_auth()` method
3. Implement `post()` method
4. Add platform name to `get_supported_platforms()`
5. Add `_handle_<platform>_auth()` method in reauth script

### Modifying Authentication Flow

Edit the `_perform_oauth_flow()` method in `ReauthManager` class to customize OAuth flows for different platforms.

## License

See project LICENSE file.
