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
