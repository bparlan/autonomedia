# Milestone M12: AI Rewrite & Platform-Level Verification

## Objective
Enable a granular AI-assisted content workflow where ideas are rewritten per-platform, verified by the user at the platform level, and released to the posting pool only upon explicit verification.

## Success Criteria
- [ ] **Granular Generation**: AI generates distinct content blocks for every platform assigned to the Idea.
- [ ] **Verification UI**: Review screen displays platform-specific content with individual verification checkboxes.
- [ ] **Platform-Level Verification**: User must verify specific platforms; only verified contents enter the `Posting_Secretary` queue.
- [ ] **Operational Control**: "Stop" functionality for items currently in the `ready_to_post` pool, effectively removing them from execution.
- [ ] **State Integrity**: `status` and `verification_status` correctly reflect the lifecycle of a post from `Idea` -> `Approved` -> `Prepared` -> `Ready`.

## Phases

### Phase 1: Infrastructure & DB
- Add `verification_status` JSONB column to `content` table.
- Define platform defaults (Mastodon, X) for `["all"]` platform configuration.

### Phase 2: AI Orchestration
- Update `AI_Planner` to iterate over platform lists.
- Generate JSON payload: `{"platform_name": "rewrite_text", ...}`.

### Phase 3: Review UI
- Render platform-specific content blocks in `review.html`.
- Add "Check-to-Verify" mechanism for each platform block.
- Add "Send Verified to Queue" button (POST `/queue-verified`).

### Phase 4: Queue Management
- Add "Remove" functionality for `ready_to_post` content.
- Update `Posting_Secretary` to filter by `verification_status`.

## Risks
- **Generation Latency**: Processing multiple platforms per item may increase generation time.
- **State Drift**: Potential mismatch if `verification_status` is updated while a background `Posting_Secretary` task is picking up the item.

## Status
- **Completed**: 2025-06-25

## Completion Notes
- All phases implemented and verified
- Findings archived to `docs/milestones/M12_FINDINGS_ARCHIVE.md`
- Platform status polling working via HTMX
- Per-platform verification enabled via `verification_status` column

