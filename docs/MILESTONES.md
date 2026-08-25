# AUTONOMEDIA - MILESTONES.md

This document tracks all project milestones, their states, and lifecycle management, aligned with the strategic roadmap.

## Milestone Lifecycle

The Spec-Driven Development (SDD) pipeline follows this exact sequence:

1. **Milestone Creation**: Milestone documented in `milestones/M{X}/M{X}.md`
2. **Specification Generation**: Specification created in `milestones/M{X}/M{X}S{Y}.md`
3. **Verification Generation**: Verification protocol created in `milestones/M{X}/M{X}S{Y}V.md`
4. **Test Generation**: Test scripts created in `tests/M{X}/` and `milestones/M{X}/M{X}S{Y}T{Z}.md`
5. **Test Evaluation**: Pre-implementation baseline validated in `milestones/M{X}/M{X}S{Y}TE.md` (must show RED state)
6. **Specification Approval**: User approval via `approve-spec` (marked in M{X}S{Y}.md frontmatter)
7. **Implementation**: Code implemented per specification (`milestones/M{X}/M{X}S{Y}C.md`)
8. **Implementation Evaluation**: Post-implementation validation (`milestones/M{X}/M{X}S{Y}E.md`)
9. **Implementation Review**: Review completed (`milestones/M{X}/M{X}S{Y}R.md`)
10. **Milestone Closure**: Loop-closure validated and closure artifact created (`milestones/M{X}/M{X}CLOSE-{N}.md`)
11. **Documentation Sync**: Review changes integrated into roadmap, changelogs, and indices
12. **Archival**: Milestone documents moved to `milestones/archive/` with full history

---

## Active & Upcoming Milestones

### Milestone 17: Repository-Wide 3-Layer Registry Pattern Enforcement
* **Focus**: Reorganizing data, view, and logic paths into a clean layered structure.
* **Deadline**: 2026-08-29
* **Target Files**:
  - `/storage/data/` (JSON registries and configs)
  - `/src/web/templates/` (Consolidated HTML templates)
  - `/src/`, `/tests/` (Logic and validation only)
* **Deliverables**:
  - Move L1 JSON registries/configs (`mention_registry.json`) to `storage/data/`.
  - Move J2 HTML templates to `src/web/templates/`.
  - Python logic strictly under `/src/` and `/tests/`.
  - Purge empty legacy folders (`tests/M18/`, `tests/M16/`, etc.).
* **Success Criteria**:
  - Directory compliance score 100% (0 stray `.py` or `.json` outside designated layers).
  - All unit tests pass in new structure.

### Milestone 18: Core "Idea" State-Machine Verification & Web App Route Stabilization
* **Focus**: Objective E2E state tests and dashboard repair.
* **Deadline**: 2026-09-05
* **Target Files**:
  - `/tests/e2e/test_state_machine_e2e.py`
  - `/src/autonomedia/web/app.py` (Active entry point)
  - `/src/web/ui/health.jsx`
* **Deliverables**:
  - Verify campaign state transitions: `idea` -> `prepared` -> `ready_to_post` -> `published`.
  - Fix entry-point fragmentation; integrate health routing into active `src/web/app.py`.
  - Bind active React `health.jsx` component to functional routes.
* **Success Criteria**:
  - 4/4 E2E state transition tests pass.
  - 100% route coverage on `app.py`.

### Milestone 19: Social Account "Tool-Use" Abstraction & Multi-Account OAuth Flow
* **Focus**: Multi-account management dashboards and dynamic posting handlers using MCP tool abstractions.
* **Deadline**: 2026-09-12
* **Target Files**:
  - `/src/autonomedia/accounts/`
  - `/src/web/ui/accounts.jsx`
  - `/src/autonomedia/api/oauth.py`
* **Deliverables**:
  - Add interactive CRUD UI ("Add Account", "Refresh Auth", "Remove Account").
  - Handle dynamic credential session states.
  - Display expired-token warning badges in the dashboard.
* **Success Criteria**:
  - OAuth flow completes without manual redirect.
  - 3+ accounts manageable via UI.
  - Token expiry badges render correctly for stale sessions.

---

## Past Milestones Ledger

### Milestone 0: Foundation & Core Idea Scheduling (MVP)
* **Goal**: Enable a solo developer to define an "Idea" and have it automatically rewritten and published on schedule to a single platform (Mastodon).
* **Status**: Completed (2026-08-24)
* **Key Components**: Idea Model, Scheduling Engine, Gemini Rewrite, Mastodon Worker.

### Milestones 1-15: Cross-Platform Expansion & Platform Visibility
* **Goal**: Unified platform abstraction layer and character limit adaptation for LinkedIn, X, and Mastodon.
* **Status**: Completed (2026-07-11)
* **Key Components**: `PlatformHandler.post()` API, Multi-platform task handlers, HTMX-driven web app routes.

---

## Development & Review Rules

1. **The Spec is Law**: Specs and verifications cannot be edited to force test passes.
2. **Surgical Edits Only**: Precision editing over broad rewrites.
3. **Iron Law of Debugging**: Diagnose root causes before modifying code.
4. **Verification**: Always run verification suites after applying fixes.
