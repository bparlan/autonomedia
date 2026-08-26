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

# FIRST IMPLEMENTATION TARGET: IDEA FEATURE MVP

Our initial MVP for the "Idea" feature will focus on a single platform to ensure stability and rapid iteration.

Start with:
1. Mastodon (for Idea posting and scheduling)

Reasoning:
-   Easier automation surfaces and API interactions.
-   Faster iteration cycle for core "Idea" feature development.
-   Lower anti-bot hostility compared to other major platforms.

DO NOT start with other platforms (LinkedIn, X, Facebook, Bluesky) for the MVP to maintain focus and minimize complexity.


# COMMON FAILURE MODES

## Idea & Content Verification Requirements

-   **E2E Testing Mandate:** Every UI feature related to `Idea` management and its content rendering (e.g., scheduled posts, AI-generated variants) must have corresponding e2e tests before merge. This includes explicit test coverage for `Idea`-specific statuses (e.g., Pending AI Rewrite, Ready to Post, Published).
-   **Command Center Visibility:** The Command Center (operational view) must expose "Unqueue" or "Retry" actions for any `Idea`-related queued item (e.g., failed AI rewrites, stalled posts) to match operational expectations.
-   **Badge Coverage Completeness:** Test assertions for dashboard badges displaying `Idea` or post status must validate:
    +- All expected statuses display (no silent omission).
    +- Verified/unverified status renders correctly for each `Idea` post.
    +- Platform names are explicitly shown for each scheduled post, not inferred.

### Human-in-the-Loop Workflow (Idea-Specific)

-   **Retry**: Triggered on AI API/parsing errors during `Idea` content generation or platform API failures (System-level failure).
-   **Regenerate**: Triggered by user for poor quality/tone of AI-generated `Idea` variants (Human-level preference).
-   The differentiation is currently inferred from the trigger context, directly impacting the `Idea`'s workflow state.

## Fragile Selectors (for Idea UI/Platform Adapters)

Fix:
- accessibility selectors for Idea management UI.
- semantic targeting for platform interaction via adapters.
- avoid CSS chains in Playwright selectors for `Idea` related actions.


## Session Corruption (for Idea Posting)

Fix:
- isolated browser profiles for each platform used by `Idea` posting.
- backup profiles for quick recovery.
- avoid shared state across `Idea` posting operations for different platforms.


## AI Overreach (for Idea Rewriting)

Fix:
- deterministic orchestration of AI rewrite module for `Idea` content.
- AI only for transformations defined by `Idea`'s `AI Style Presets`.
- Strict adherence to `Whitelist Contact Truth Registry` for `Idea` content.


## Logging Blindness (for Idea Workflow)

Fix:
- structured logs for every step of the `Idea` lifecycle (creation, scheduling, rewriting, posting, analytics).
- screenshots at critical points of `Idea` posting workflow.
- detailed verification steps for `Idea` publication.

### Silent Platform Exclusion Logging (for Idea Posts)

Platforms excluded from `Idea` posting due to unhealthy status or missing verification must be logged explicitly with context. Include:
- platform name
- idea_id (or post_id)
- exclusion reason

This ensures auditability for platforms silently removed from `Idea` posting queues.

# WEB DEVELOPMENT WORKFLOW

## UI Framework Strategy & Development (Idea-Centric)

As defined in `FRAMEWORK.md`, Autonomedia employs a hybrid UI framework strategy. When implementing new `Idea` management features or dashboards:

### 1. Design Phase:

-   **Determine UI Framework:** Prefer React for complex, interactive dashboards and dynamic data visualization (e.g., advanced analytics, real-time status updates, intricate `Idea` management interfaces). Use Jinja2 templates for simpler, server-rendered pages (e.g., static content, basic forms).

### 2. Implementation Phase:

-   **React Components:** Create in `src/autonomedia/web/ui/` for complex `Idea` dashboards.
-   **Jinja2 Templates:** Create in `src/autonomedia/web/templates/` for simpler `Idea` related pages.
-   **API Endpoints:** Implement in `src/autonomedia/api/` (for data) and `src/autonomedia/web/router.py` (for UI-specific routes).
-   **Integration:** Integrate into `src/autonomedia/web/main.py` router using FastAPI patterns.

### 3. Testing Phase:

-   **Comprehensive Tests:** Write tests for happy paths and error paths for both UI and API, specifically for `Idea` creation, scheduling, and management.
-   **UI Rendering:** Verify dashboard renders correctly (React components) or templates display correctly (Jinja2).
-   **API Data Integrity:** Verify API returns correct JSON for `Idea` data and actions.
-   **Data Binding:** Test data binding between frontend and backend for `Idea` entities.

### 4. Integration Phase:

-   **Route Registration:** Ensure all `Idea` related routes are registered in the main app.
-   **Accessibility:** Verify endpoints are accessible and functional.
-   **Environment Testing:** Test in both development and production environments.
-   **Documentation:** Update relevant documentation (`SPEC.md`, `PLAYBOOK.md`) as needed.

## Common Pitfalls (Idea-Centric UI Development)

### Wrong Entry Point
-   **Problem:** Implementing `Idea` related routes in `src/autonomedia/web/server.py` instead of `src/autonomedia/web/main.py`.
-   **Solution:** Always integrate `Idea` features into the main app (`src/autonomedia/web/main.py`).

### Architecture Deviation
-   **Problem:** Hardcoding HTML for complex `Idea` dashboards instead of using React components when appropriate.
-   **Solution:** Adhere to the hybrid UI strategy: React for dynamic `Idea` dashboards; Jinja2 templates for simpler pages.

### Duplicate Routes
-   **Problem:** Creating duplicate `/ideas` or similar endpoints with conflicting behavior.
-   **Solution:** Use a single entry point for `Idea` management; rename if needed.

### Missing Tests
-   **Problem:** `Idea` UI or API changes without corresponding tests.
-   **Solution:** Always write tests before/after changes, focusing on `Idea` lifecycle.


# FAILURE MODE: SILENT STUB EXECUTION (IDEA POSTING)
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

# DEVELOPMENT REVIEW RULES

If the review fails, the agent must abide by these rules when applying fixes:

1. **The Spec is Law:** You cannot change the `docs/specs/` or `docs/verifications/` files to make the tests pass. If the code cannot meet the spec, the code is wrong.

2. **Surgical Edits Only:** Do not rewrite entire files to fix a minor issue. Use the `edit` tool to specifically target the broken lines.

3. **Iron Law of Debugging:** If tests are failing, diagnose the root cause *before* changing code. Form a hypothesis, and test one hypothesis at a time.

4. **Run Tests After Every Fix:** You must run `just test` and verify the `exitCode` before deciding a revision is complete.

# M18S5 Implementation Procedures

## Overview
This document outlines the procedures and workflows implemented during the M18S5 milestone for Infrastructure Health Dashboard verification protocol optimization.

## Implementation Steps

### 1. Pre-implementation
- Validate specification requirements (SPEC-M18S5)
- Execute test evaluation (M18S5TE.md)
- Approve specification (user approval stamp)

### 2. Implementation
- Apply specification to codebase via implement-specification
- Execute evaluation-implementation (M18S5E.md)
- Perform review-implementation (M18S5R.md)
- Complete loop-closure validation (M18S5CLOSE-1.md)

### 3. Post-implementation
- Run documentation sync (sync-documentation)
- Archive completed artifacts (close-milestone)
- Update project documentation (sync-documentation)

## M18S5 Specific Procedures

### Browser-based React Component Validation
- Execute Playwright E2E tests: `python3 -m playwright test tests/M18/test_health_dashboard_binding_e2e.py`
- Validate React component integration in browser environment
- Ensure proper error handling and state management

### Environment Configuration
- Set BASE_URL environment variable for all test scripts
- Configure Playwright browser automation
- Verify React component server integration

### Quality Gates
- Metadata validation (validate_metadata.py)
- Lint evaluation gate (lint-evaluation-gate.py)
- Artifact completeness verification
- Loop-closure validation

## Documentation Sync Workflow

### Pre-ingestion Requirements
- All milestone artifacts must be present (SPEC, VER, TSET, TE, C, E, R, CLOSE)
- User approval must be stamped in specification
- Loop-closure validation must pass

### Post-ingestion Process
1. Scan all M18S5 artifacts
2. Compare against SPEC.md, DATA.md, PLAYBOOK.md, CHANGELOG.md
3. Update canonical documentation
4. Regenerate architecture diagrams (MANDATORY)
5. Present all changes for user approval

### Diagram Regeneration
- Execute diagrammer skill to rebuild docs/diagrams/system_snapshot.mmd
- Validate diagram against current codebase structure
- Present diagram changes for approval

## M18S5 Artifact Lineage

```
M18S5.md (SPEC) → M18S5V.md (VER) → M18S5T1.md (TSET)
     ↓                                  ↓
M18S5E.md (EVAL) ←─── M18S5TE.md (TE) ←─── M18S5C.md (COMPLETION)
     ↓
M18S5R.md (REVIEW) ←─── M18S5CLOSE-1.md (CLOSURE)
```

## Next Steps

1. Execute Playwright E2E tests for React component validation
2. Verify environment variable configuration
3. Update documentation with M18S5-specific procedures
4. Ensure all quality gates pass
5. Archive completed milestone artifacts

## Verification Commands

```bash
# Test React component validation via browser automation
python3 -m playwright test tests/M18/test_health_dashboard_binding_e2e.py

# Validate API endpoint with environment variable
BASE_URL="http://localhost:8000" bash tests/M18/test_health_endpoint.sh

# Verify dashboard accessibility
BASE_URL="http://localhost:8000" bash tests/M18/test_health_dashboard_ui.sh

# Validate healthcheck utility
python3 tests/M18/test_healthcheck_utility.py

# Verify implementation evaluation
python3 ~/devcode/aef/agent/bin/validate_metadata.py milestones/M18/M18S5.md milestones/M18/M18S5V.md milestones/M18/M18S5E.md milestones/M18/M18S5C.md
```

## Archive

- `docs/skills.md` - Updated with sync-documentation skill
- `docs/PLAYBOOK.md` - Added M18S5 implementation procedures
- `docs/diagrams/system_snapshot.mmd` - Regenerated architecture overview


## M18S5 Implementation Procedures


### Implementation Overview

The M18S5 milestone implemented Infrastructure Health Dashboard verification protocol optimization to eliminate technical debt and adapt to client-side React architecture.

### Key Deliverables

- Browser-based React component validation via Playwright
- Environment variable BASE_URL usage in all test scripts
- Zero hardcoded localhost:8000 references in test files
- Generated verification protocol M18S5V.md
- Only allowlist files modified, denylist files remain untouched
- Browser-based React component validation replaces static HTML pattern matching
