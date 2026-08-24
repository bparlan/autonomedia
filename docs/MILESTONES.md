# AUTONOMEDIA - MILESTONES.md

This document tracks all project milestones, their states, and lifecycle management, aligned with the strategic roadmap.

## Milestone Lifecycle

The Spec-Driven Development (SDD) pipeline follows this exact sequence:

1.  **Milestone Creation**: Milestone documented in `milestones/M{X}/M{X}.md`
2.  **Specification Generation**: Specification created in `milestones/M{X}/M{X}S{Y}.md`
3.  **Verification Generation**: Verification protocol created in `milestones/M{X}/M{X}S{Y}V.md`
4.  **Test Generation**: Test scripts created in `tests/M{X}/` and `milestones/M{X}/M{X}S{Y}T{Z}.md`
5.  **Test Evaluation**: Pre-implementation baseline validated in `milestones/M{X}/M{X}S{Y}TE.md` (must show RED state)
6.  **Specification Approval**: User approval via `approve-spec` (marked in M{X}S{Y}.md frontmatter)
7.  **Implementation**: Code implemented per specification (`milestones/M{X}/M{X}S{Y}C.md`)
8.  **Implementation Evaluation**: Post-implementation validation (`milestones/M{X}/M{X}S{Y}E.md`)
9.  **Implementation Review**: Review completed (`milestones/M{X}/M{X}S{Y}R.md`)
10. **Milestone Closure**: Loop-closure validated and closure artifact created (`milestones/M{X}/M{X}CLOSE-{N}.md`)
11. **Documentation Sync**: Review changes integrated into roadmap, changelogs, and indices
12. **Archival** (Optional): Milestone documents moved to `milestones/archive/` with full history

### Fix Paths (when evaluation fails):
- **Hotfix Issue**: For MINOR_IMPLEMENTATION_DEFECT → loops back to evaluation
- **Investigate Issue**: For COMPLEX_OR_UNCLEAR_ISSUE → loops back to evaluation
- Both paths MUST return through evaluation before proceeding to review

## Active & Upcoming Milestones

### Milestone 0: Foundation & Core Idea Scheduling (MVP)

*   **Goal:** Enable a solo developer to define an "Idea" and have it automatically rewritten and published on schedule to a single platform (Mastodon).
*   **Status:** Completed (2026-08-24)
*   **Key Deliverables:**
    *   Idea Data Model implemented in `src/autonomedia/database/schema.py` and CRUD operations in `src/autonomedia/database/client.py`.
    *   Basic Scheduling Engine for custom intervals in `src/autonomedia/core/scheduler.py`.
    *   AI Rewrite Module (base and Gemini-specific) in `src/autonomedia/ai/rewriting/`.
    *   Mastodon Posting Worker in `src/autonomedia/platforms/mastodon/`.
    *   System Map Documentation: Data Flow, UI Flow (Content Creator Journey), Interaction Matrix (`docs/system_map_data_flow.md`, `docs/system_map_ui_flow.md`, `docs/system_map_interaction_matrix.md`).
    *   Release Report summarizing implementation and open issues (`docs/system_map_release_report.md`).
*   **Related Docs:** `docs/SPEC.md`, `docs/FRAMEWORK.md`, `docs/PLAYBOOK.md`, `docs/ROADMAP.md` (updated).

### Milestone 1: Multi-Platform Expansion & Authentication

*   **Goal:** Extend Idea publishing to multiple platforms and handle authentication securely.
*   **Status:** Upcoming
*   **Key Deliverables:**
    *   Platform Abstraction Layer refinements.
    *   Secure OAuth 2.0 implementation for LinkedIn and X.
    *   LinkedIn and X Platform Handlers.
    *   UI integration for multi-platform selection.

### Milestone 2: Advanced AI & Content Control

*   **Goal:** Enhance AI capabilities for more nuanced content generation and user control.
*   **Status:** Upcoming
*   **Key Deliverables:**
    *   Advanced AI Style Presets and fine-tuning options.
    *   Robust Content Validation Engine.
    *   UI for managing and customizing the Whitelist Registry.

### Milestone 3: Analytics, Monitoring & Refinement

*   **Goal:** Provide deep insights into Idea performance and improve system reliability.
*   **Status:** Upcoming
*   **Key Deliverables:**
    *   Engagement Data Ingestion.
    *   Comprehensive Analytics Dashboard.
    *   Enhanced System Health Monitoring.
    *   Advanced Error Handling and Retry Mechanisms.

### Milestone 4: Extensibility & Future Growth

*   **Goal:** Prepare the system for future expansion and integration of new capabilities.
*   **Status:** Upcoming
*   **Key Deliverables:**
    *   Plugin Architecture for new AI models and platform adapters.
    *   Refined API for external integrations.
    *   Initial User Management features.

### M18 - Infrastructure Health Dashboard

*   **Current Phase:** Review and Correction (Deferred)
*   **Status:** In Progress (Needs significant refactoring to align with current architecture)
*   **Outstanding Work (Re-prioritized):**
    *   Integrate dashboard into `src/autonomedia/web/app.py` (Correct entry point).
    *   Merge React and HTML implementations (Align with frontend strategy).
    *   Resolve duplicate `/health` endpoints.
    *   Address evaluation report inaccuracy and missing metadata.
*   **Note:** Resolution of M18 will be re-evaluated after the completion of core MVP-related milestones. Its current state does not block the "Idea" feature development.

## Archived Milestones

*   **M15 - Cross-Platform Expansion (Archived):** Concepts from this milestone have been integrated into Milestone 1 of the new roadmap.
*   **M16 - Automated Testing and Use-Case Generation Framework (Active -> Archived):** This milestone's goals are now integrated into the standard SDD verification process across all new milestones.
*   **M14 - Daily Posting Routine with Randomized Intervals (Archived):** Functionality superseded by the new "Idea" scheduling engine.
*   **M13 - Ready to Publish Platform Visibility (Archived):** Replaced by integrated UI/analytics within the new milestone structure.
*   **M12 - Granular Platform Verification (Archived):** Concepts are now part of the Content Validation Engine (Milestone 2).
*   **M11 - Observability & Self-Healing (Archived):** Core concepts integrated into Milestone 3 (Analytics, Monitoring & Refinement).
*   **M10 - Autonomous Runtime (Archived):** Foundational work on async architecture and browser profiles is now an inherent part of the system's runtime.
*   **M7 - Moderation & Guardrails (Archived):** Content validation aspects are now part of Milestone 2 (Advanced AI & Content Control).
*   **M6 - AI & Assembly Line (Archived):** AI rewrite and posting worker concepts integrated into Milestone 0 (MVP).
*   **M5 - Content Generation (Archived):** Superseded by the "Idea" feature's content generation.
*   **M4 - Browser Setup (Archived):** Fundamental browser setup now part of system infrastructure.
*   **M3 - Initial Deployment (Archived):** Project deployment is now part of general operations.
*   **M2 - Schema Design (Archived):** Database schema design is now an ongoing task within feature development.
*   **M1 - Foundation (Archived):** Project initialization is now part of standard setup.

*All milestone files, including those mentioned above, are preserved in `milestones/archive/` with complete history.*

- ### M18 - Infrastructure Health Dashboard (In Progress → milestones/M18/)
- ### M15 - Cross-Platform Expansion (Archived)
- ### M16 - Automated Testing and Use-Case Generation Framework (Active)


**Status:** Completed  
**Spec:** M15  
**Archive:** milestones/archive/M15/  
**Verification:** M15S1V, M15S2V, M15S3V, M15S4V  
**Review:** M15S1R, M15S2R, M15S4R  
**Completion:** M15S1C, M15S2C, M15S3C, M15S4C  

**Completed Requirements:**
- Unified platform abstraction layer with `post()` API for Mastodon, LinkedIn, and X
- Platform-specific task handlers deployed and tested
- Platform requirements documentation created (M15S3)
- Platform constraints API with character limits and validation
- Content adaptation utilities for multi-platform posting
- Reauthentication management script with CLI tools
- Production deployment and monitoring documentation
- Comprehensive platform-specific guidance (M15S2, M15S3)

**Known Limitations:**
- Integration test suite has 29 failing tests (test assertions mismatch implementation signatures)
- OAuth 2.0 browser flows implemented as placeholders in reauth script
- Health check HTTP endpoints documented but not implemented
- Real-time monitoring dashboard documented but not implemented
- Token management via environment variables (no encrypted vault support)

**Critical Issues Identified:**
- Missing return statement in `XHandler.format_tweet()` (M15I1)
- Missing `get_rate_limit_status()` method in handlers (M15I1)
- Incomplete OAuth flow implementations in reauth script (M15I1, M15I2)

**Documentation:**
- Platform requirements: `docs/platform_requirements.md`
- Deployment guide: `docs/deployment_guide.md`
- ---
- ### M18 - Infrastructure Health Dashboard (In Progress → milestones/M18/)
-
- **Status:** In Progress (Test Implementation Phase)
- **Spec:** M18S1
- **Verification:** M18S1V
- **Review:** M18S1R, M18S1_FINDINGS.md
- **Active Tests:** test_health_endpoint.sh, test_health_dashboard_ui.sh, test_health_dashboard_binding.sh
-
- **Completed Requirements:**
- - API endpoint handler created (`get_health_status()`)
- - Router registered with `/api/health` route
- - React dashboard component created (`health.jsx`)
- - HTML dashboard template created (`health.html`)
- - Basic server integration in `src/autonomedia/web/server.py`
-
- **Known Limitations:**
- - Wrong entry point: Dashboard implemented in inactive `src/autonomedia/web/server.py` instead of `src/web/app.py`
- - Architecture deviation: React component not integrated; hardcoded HTML template is being served
- - Duplicate /health endpoints: Two conflicting endpoints exist with different behaviors
- - Evaluation report discrepancy: Claims tests passed, actual execution shows failures
- - Missing metadata: Milestone contract lacks required `id` field
- - No completion report: M18S1C.md not generated
-
- **Critical Issues Identified:**
- - FIND-001: Wrong entry point integration (src/web/app.py is active, server.py is not)
- - FIND-002: Dashboard architecture deviation (React not integrated)
- - FIND-003: Evaluation report inaccuracy (tests fail in current environment)
- - FIND-004: Missing milestone contract ID
- - FIND-006: Duplicate /health endpoints with conflicting behavior
-
- **Documentation:**
- - Specification: `milestones/M18/M18S1.md`
- - Verification: `milestones/M18/M18S1V.md`
- - Review: `milestones/M18/M18S1_REVIEW.md`
- - Findings: `milestones/M18/M18S1_FINDINGS.md`

---

### M14 - Daily Posting Routine with Randomized Intervals (Archived → milestones/archive/M14/)

**Status:** Completed
**Archive:** milestones/archive/M14.md, milestones/archive/M14S1.md, milestones/archive/M14S1V.md, milestones/archive/M14S1R.md
**Verification:** M14S1V  
**Review:** M14S1R  

**Completed Requirements:**
- Randomized delay system (2-10 minutes between batches)
- Verification status filtering for mastodon
- Max 1-2 items per execution with 8-hour window
- `expires_at` TTL field (12 hours default)
- Manual trigger script `run_daily_posting.py`
- Dry-run mode

- Legacy `PostingWorker` still present without verification checks

---

### M13 - Ready to Publish Platform Visibility (Archived → milestones/archive/M13/)

**Status:** Completed  
**Specs:** M13S1, M13S2, M13S3, M13S4  
**Archive:** milestones/archive/M13.md, milestones/archive/M13S1.md, M13S1R.md, M13S1V.md, M13S2.md, M13S2R.md, M13S2V.md, M13S3.md, M13S3R.md, M13S3V.md, M13S4.md, M13S4R.md, M13S4V.md

**Completed Requirements:**
- Per-platform verification status in dashboard
- Verified state badges
- Backend query modifications for `ready_to_post` items
- Frontend ready-to-publish rows
- Platform health filtering

---

### M12 - Granular Platform Verification (Archived → milestones/archive/M12/)

**Status:** Completed  
**Spec:** M12  
**Archive:** milestones/archive/M12.md, milestones/archive/M12-findings.md

**Completed Requirements:**
- `verification_status` JSONB column on `content` table
- Per-platform approval workflow
- `PostingSecretary.process_verified_content()` filtering
- Platform dispatch integration

---

### M11 - Observability & Self-Healing (Archived → milestones/archive/M11/)

**Status:** Completed  
**Archive:** milestones/archive/M11.md, milestones/archive/M11-OBSERVABILITY-AND-SELF-HEALING.md, milestones/archive/M11-Verify.md, milestones/archive/M11-Review.md, milestones/archive/M11.md

**Completed Requirements:**
- Structured runtime logging
- Error resolution and auto-retry
- Session health monitoring
- Failure capture (screenshots, logs, DOM snapshots)

---

### M10 - Autonomous Runtime (Archived → milestones/archive/M10/)

**Status:** Completed  
**Archive:** milestones/archive/M10.md, milestones/archive/M10-AUTONOMOUS-RUNTIME.md, milestones/archive/M10-VERIFICATION.md, milestones/archive/M10-Verify.md, milestones/archive/M10-review.md, milestones/archive/M10.md

**Completed Requirements:**
- Async Assembly Line architecture
- Browser profile isolation
- Playwright anti-detection profiles
- Human-like pacing and randomized delays

---

### M9 - Platform Health & Analytics (Archived → milestones/archive/M9/)

**Status:** Completed  
**Archive:** milestones/archive/M9.md, milestones/archive/findings_M9.md

**Completed Requirements:**
- Session health tracking
- Failed post logging
- Platform status visibility
- Analytics integration

---

### M8 - Domain Extraction & UX (Archived → milestones/archive/M8/)

**Status:** Completed  
**Archive:** milestones/archive/M8.md

**Completed Requirements:**
- Domain extraction UI
- Command Center (inbox view)
- Content management backlogs
- AI review workflow

---

### M7 - Moderation & Guardrails (Archived → milestones/archive/M7/)

**Status:** Completed  
**Archive:** milestones/archive/M7.md

**Completed Requirements:**
- ModerationAdapter for content validation
- Browser anti-detection profiles
- Duplicate post prevention
- Human-in-the-loop review

---

### M6 - AI & Assembly Line (Archived → milestones/archive/M6/)

**Status:** Completed  
**Archive:** milestones/archive/M6.md

**Completed Requirements:**
- AI rewrite generation with Gemini
- Assembly Line state machine
- PostingSecretary (AI Worker)
- PostingExecutor (Browser Worker)

---

### M5 - Content Generation (Archived → milestones/archive/M5B/, M5C/, M5X/)

**Status:** Completed  
**Archive:** milestones/archive/M5B.md, milestones/archive/M5C.md, milestones/archive/M5X.md

**Completed Requirements:**
- Content idea generation
- AI rewrite generation
- Platform-specific transformations

---

### M4 - Browser Setup (Archived → milestones/archive/M4/)

**Status:** Completed  
**Archive:** milestones/archive/M4.md

**Completed Requirements:**
- Playwright setup
- Browser profile persistence
- Basic routing

---

### M3 - Initial Deployment (Archived → milestones/archive/M3/)

**Status:** Completed  
**Archive:** milestones/archive/M3.md

**Completed Requirements:**
- Initial deployment
- Basic infrastructure

---

### M2 - Schema Design (Archived → milestones/archive/M2/)

**Status:** Completed  
**Archive:** milestones/archive/m2_technical_specifications.md

**Completed Requirements:**
- Database schema design
- Content model definition

---

### M1 - Foundation (Archived → milestones/archive/M1/)

**Status:** Completed  
**Archive:** milestones/archive/M1_Content_Idea_Ingestion_AI_Analysis.md

**Completed Requirements:**
- Project initialization
- Basic structure setup

---

- ## Milestone Lifecycle
-
- 1. **Proposal**: Milestone documented in `specs/` directory
- 2. **Implementation**: Code and tests added per specification
- 3. **Verification**: Verification document created in `verifications/` directory
- 4. **Review**: Review document created in `reviews/` directory
- 5. **Approval**: Milestone approved by team
- 6. **Completion**: All requirements verified, code merged
- 7. **Archival**: Moved to `milestones/archive/` with full documentation
-
- ## Active Milestones
-
- ### M18 - Infrastructure Health Dashboard
-
- **Current Phase:** Review and Correction
- **Previous Phase:** Test Implementation (M18S1TE.md)
- **Next Phase:** Implementation Fix and Re-verification
-
- **Outstanding Work:**
- 1. Integrate dashboard into `src/web/app.py`
- 2. Fix evaluation report accuracy
- 3. Add `id` field to M18.md
- 4. Generate M18S1C.md completion report
- 5. Resolve duplicate /health endpoints
- 6. Merge React and HTML implementations
- 7. Fix test set YAML parsing
- 8. Re-run and verify tests

## Notes

- All milestone files are preserved in `milestones/archive/` with complete history
- Archive directory is organized by milestone with separate subdirectories for specs, verifications, and reviews when applicable
- Raw artifacts (test outputs, verification logs) stored in `milestones/archive/raw_artifacts/`

## Known Issues & Lessons Learned

### M14 - Daily Posting Routine with Randomized Intervals





1. **Legacy Code Path Conflict Risk**
   - Issue: `PostingWorker` in `posting_executor.py` exists alongside `posting_routine()`. Both can query `ready_to_post` without coordination. M14S1 spec states old worker "posts content regardless of platform verification state."
   - Recommendation: Either deprecate `PostingWorker` or add a compatibility layer that prevents simultaneous execution.
   - Status: Potential operational hazard if both workers are active.

# DEVELOPMENT REVIEW RULES

If the review fails, the agent must abide by these rules when applying fixes:

1. **The Spec is Law:** You cannot change the `docs/specs/` or `docs/verifications/` files to make the tests pass. If the code cannot meet the spec, the code is wrong.

2. **Surgical Edits Only:** Do not rewrite entire files to fix a minor issue. Use the `edit` tool to specifically target the broken lines.

3. **Iron Law of Debugging:** If tests are failing, diagnose the root cause *before* changing code. Form a hypothesis, and test one hypothesis at a time.

4. **Run Tests After Every Fix:** You must run `just test` and verify the `exitCode` before deciding a revision is complete.


