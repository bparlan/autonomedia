# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.2] — 2026-06-28

### Fixed
- Consolidated duplicate verification parsing logic into shared utility `src/autonomedia/core/utils/verification.py`
  - `parse_verification_status()`: handles string/dict parsing from DB
  - `is_platform_verified()`: checks platform verification status
  - `get_platform_verification()`: gets platform data with defaults
  - `get_verified_at_timestamp()`: extracts timestamp for sorting
- **Optimized Query**: Pushed verification status filtering and sorting to the database using JSONB operators in `_get_verified_content` function in `src/autonomedia/core/posting_routine.py`.
- **Added Index**: Created `idx_content_verified_mastodon` index on `content.verification_status` for efficient querying.

### Verified
- All tests passing after refactoring


## [0.7.1] — 2026-06-28

### Fixed
- M13 template data model mismatch: `verification_status["platform"]["verified"]` instead of `verification_status["platform"] == true`
- Updated dashboard.html and content_row.html to correctly access nested verification structure
- Fixed test assertions to match production data format (nested dict with verified/verified_at/expires_at)

### Verified
- All 48 M12/M13/M14 tests passing
- Per-platform badges render correctly in dashboard and rewrites views

## [0.7.0] — 2026-05-25

### Added
- M13S2: Backend Query Modifications
  - `/rewrites` endpoint now includes `ready_to_post` status items
  - Added `/prepared-content/{id}` read-only endpoint for per-platform content preview
  - Approve endpoint filters to only healthy platforms (`platform_health.is_healthy = TRUE`)
  - Unqueue action clears `verification_status = '{}'::jsonb`
- M13S3: Frontend Ready to Publish Per-Platform Rows
  - Per-platform row rendering in dashboard Ready to Publish section
  - Content preview truncated at 100 chars with `text-xs` styling
  - Green badge for verified platforms, gray for unverified/pending
- M13S4: AI Rewrite Dashboard Verified State
  - Platform Status column shows per-platform verification badges
  - Platform labels on badges (e.g., "Mastodon: Verified - In Queue")
  - Graceful handling for malformed verification_status JSON

### Fixed
- M13S2 fixes applied during review:
  - Added `FOR UPDATE` to status check for atomic concurrent approvals (TC07)
  - Consolidated redundant platform filtering into single-pass logic
  - Added logging for unhealthy platform exclusions
- Updated UI for per-platform verification and post-queueing.
- Updated task handling in Posting Secretary and added stale-task cleanup.
- Updated documentation: TASK PLAN, M12 milestone spec, UI templates.
- Minor bug fixes (NameError, typo handling).

## [0.6.0] — 2026-05-23

### Added
- AI Rewrite Adapter (`RewriteProvider`) with Gemini fallback chain
- Assembly Line state machine (idea -> approved -> prepared -> published)
- `PostingSecretary` (AI Worker) & `PostingExecutor` (Browser Worker)
- CRUD Dashboard with delete-confirmation and form validation

### Fixed
- Migrated schema to support stateful content staging
- JSONB content parsing in dashboard
- Resolved Gemini 404 deprecation via dynamic fallback models

## [0.5.0] — 2026-05-23

### Added
- Persistent Playwright browser sessions for Mastodon publishing
- Compose automation with post verification loop
- Screenshot observability for debugging
- Runtime/profile isolation for worker-oriented execution

### Architecture
- Runtime state moved outside `src/`
- Human-approved git workflow enforced
- Worker-oriented execution model introduced

### Known Issues
- Selector fragility in Playwright automation
- No retry queue for failed posts
- No structured persistence layer

## [0.4.0] — 2026-05-22

### Added
- persistent Mastodon browser profiles
- autonomous post publishing
- screenshot verification pipeline
- structured worker runtime

### Fixed
- deterministic filesystem path resolution

### Architecture
- migrated to src-layout
- established observability layer

### M8-M11 Summary
Completed autonomous operations cycle: UX (M8), Platform Health & Analytics (M9), Runtime Autonomy (M10), and Observability/Self-Healing (M11).

### M12 Summary (Completed 2026-06-28)
- `verification_status` JSONB column on `content` table for per-platform approval
- `PostingSecretary.process_verified_content()` filters by verification status
- `/review/{id}/approve` endpoint sets verification status and transitions to `ready_to_post`
- `/remove-from-queue/{id}` endpoint provides operational control for queued items
- Platform dispatch integration for Mastodon