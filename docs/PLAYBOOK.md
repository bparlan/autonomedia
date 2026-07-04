# AUTONOMEDIA — PLAYBOOK.md

# DEVELOPMENT RULES

1. Build smallest working version first.
2. Prefer inspectability over cleverness.
3. Avoid abstraction until repeated pain appears.
4. Keep AI layer thin and strictly moderated.
5. Preserve platform isolation.
6. Always capture failures (Screenshots, Logs).
7. Prefer boring reliability.

---

# UX/UI RULES

1. **Extract Domains:** Do not cram all operations into a monolithic table or an infinite scrolling screen.
2. **Command Center is an Inbox:** The root view should only contain items that require human operator action (approvals, failed jobs, quick triage).
3. **One-Click Resolutions:** Design flows so that fixing a failure or approving a post takes exactly one click from the operational view.
4. **AI is a Workflow:** Do not treat AI review as a single HTML box. It requires diffs, traces, and platform-specific checks. Build it as a first-class subsystem.

---

# FIRST IMPLEMENTATION TARGET

DO NOT start with:
- LinkedIn
- X
- Facebook

Start with:
1. Mastodon
2. Bluesky

Reason:
- easier automation surfaces
- faster iteration
- lower anti-bot hostility

---

# COMMON FAILURE MODES

## Dashboard Verification Requirements

* **E2E Testing Mandate:** Every dashboard rendering feature must have corresponding e2e tests before merge. Per-platform dashboard status (e.g., Ready to Publish) requires explicit test coverage.
* **Unqueue Visibility:** The Command Center must expose "Unqueue" actions for any queued item to match roadmap operational expectations.
* **Badge Coverage Completeness:** Test assertions for dashboard badges must validate:
  - All expected platforms display (no silent omission)
  - Verified/unverified status renders correctly
  - Platform names are explicitly shown, not inferred

### Human-in-the-Loop Workflow

* **Retry**: Triggered on AI API/parsing errors (System-level failure).
* **Regenerate**: Triggered for poor quality/tone (Human-level preference).
* The differentiation is currently inferred from the trigger context.

## Fragile Selectors

Fix:
- accessibility selectors
- semantic targeting
- avoid CSS chains

---

## Session Corruption

Fix:
- isolated profiles
- backup profiles
- avoid shared state

---

## AI Overreach

Fix:
- deterministic orchestration
- AI only for transformations

---

## Logging Blindness

Fix:
- structured logs
- screenshots
- verification steps

### Silent Platform Exclusion Logging

Platforms excluded due to unhealthy status or missing verification must be logged explicitly with context. Include:
- platform name
- content_id  
- exclusion reason

This ensures auditability for platforms silently removed from posting queues.

---

## FAILURE MODE: SILENT STUB EXECUTION

**Symptom:** Async workers complete with log entries but no real-world effect occurs (e.g., posts not published).

**Cause:** Implementation stubbed the dispatch logic—updating internal state (database) instead of external actions (API calls).

**Detection:**
- Audit logs show status changes but no corresponding platform API logs.
- E2E tests involving real publishing fail while unit tests pass.

**Mitigation:** Require every async queue processor to have a `dispatch_to_platform()` or similar function call before any `status = 'posted'` update.

---

# IMPORTANT ARCHITECTURAL WARNING

Do not accidentally build:
- Hootsuite clone
- LangChain maze
- autonomous swarm system
- recursive self-improving agent

Build:
- operationally reliable publishing infrastructure.
