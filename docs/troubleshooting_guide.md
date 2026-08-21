# Troubleshooting Guide

| Property | Value |
|----------|-----|
| Document Type | Troubleshooting Guide |
| Derived From | M15S4 |
| Version | 1.0 |

---

## Common Errors and Solutions

### Authentication Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Token expired or invalid | Run reauth: `python reauth_script.py --platform <name>` |
| `403 Forbidden` | Token revoked or scope mismatch | Regenerate token with correct scopes |
| `Token not found` | Token not configured | Set environment variable `LINKEDIN_AUTH_TOKEN` etc. |
| `OAuth flow failed` | Browser/Docker issue | Check `/runtime/browser_profiles/` permissions |

### Rate Limit Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit exceeded | Wait for cooldown, check rate limit headers |
| `Rate limit exceeded` | Posting too frequently | Reduce posting frequency in config |
| `Backoff triggered` | Multiple failures | Review error logs, adjust timing |

### Performance Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Slow publishing | High queue backlog | Check database connections, increase workers |
| Memory pressure | Large content batches | Reduce batch size in posting config |
| Browser timeout | Headless browser stalled | Restart browser provider service |

---

## Authentication Troubleshooting

### Checking Token Status

```bash
# Check all platforms
python reauth_script.py --check-status

# Check specific platform
python reauth_script.py --platform linkedin --check
```

### Reauthentication Workflow

1. **Start reauth**:
   ```bash
   python reauth_script.py --platform linkedin --reauth
   ```

2. **Browser opens** automatically for OAuth flow

3. **Complete login** in browser window

4. **Token validated** and stored

5. **Status updated** in system

### Token Expiration

Tokens expire:
- LinkedIn: 60 days
- X: Variable (check response headers)
- Mastodon: No strict expiration

Set up alerts for tokens expiring within 7 days.

---

## Rate Limit Troubleshooting

### Checking Rate Limits

```bash
# View current rate limit status
python reauth_script.py --check-rates

# View in logs
grep "rate_limit" /storage/logs/publishing.log
```

### Rate Limit Headers

| Platform | Header | Limit |
|----------|--------|-------|
| LinkedIn | `X-RateLimit-Remaining` | 100/hr |
| X | `x-rate-limit-remaining` | 300/3hr |
| Mastodon | N/A | Polite usage |

### Backoff Strategy

System implements exponential backoff:
- First failure: 1s delay
- Second: 2s, 4s, 8s, 16s, up to 60s max

---

## Platform-Specific Issues

### LinkedIn

**Issue**: "Profile access restricted"
- Cause: Anti-detection browser profile blocked
- Solution: Rotate browser profile, reduce posting frequency

**Issue**: "Content violates policies"
- Cause: AI-detection patterns triggered
- Solution: Review content for anti-detection compliance, vary posting times

### X (Twitter)

**Issue**: "Duplicate content"
- Cause: Similar posts detected
- Solution: Use `adapt_content_for_platform()` for uniqueness

**Issue**: Image upload fails
- Cause: Invalid media format or size
- Solution: Use JPG/PNG, under 5MB

### Mastodon

**Issue**: "Visibility not supported"
- Cause: Instance feature not available
- Solution: Use standard visibility (public/unlisted)

**Issue**: "Server timeout"
- Cause: Instance overloaded
- Solution: Retry with backoff, use different instance

---

## Performance Troubleshooting

### Dashboard Loading Slowly

1. Check database connection pool
2. Verify Redis connectivity
3. Review log volume (90-day retention)

### Publishing Delays

1. Check queue size: `redis-cli LLEN publishing_queue`
2. Check worker status: `docker compose ps`
3. Review rate limits for all platforms

### High Memory Usage

1. Reduce batch size in config
2. Increase container memory limits
3. Enable swap if needed

---

## Monitoring and Alerting

### Alert Types

| Alert | Condition | Action |
|-------|-----------|--------|
| Low Success Rate | <80% posts succeed | Check platform status |
| Rate Limit High | >80% utilization | Reduce posting frequency |
| Token Expired | Token invalid | Run reauthentication |
| System Down | Health check fails | Check service status |

### Testing Alerts

```bash
# Test Slack alert
python -c "from autonomedia.core.platform.monitoring import test_alert; test_alert('slack')"

# Test email alert
python -c "from autonomedia.core.platform.monitoring import test_alert; test_alert('email')"
```

---

## Contact Support

### Internal Support

- **#ops channel** on Slack
- **@autonomedia-ops** email

### Platform Support

- LinkedIn Developer Portal: https://www.linkedin.com/developers/
- X Developer Portal: https://developer.twitter.com/
- Mastodon: Contact instance admin

### Emergency Procedures

1. **System down**: Switch to backup instance
2. **Token compromised**: Regenerate all tokens immediately
3. **Rate limit banned**: Contact platform support, reduce posting volume