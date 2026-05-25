# Task Plan: AI Rewrite Milestone (M12)

## Goal
Implement a production-grade AI Rewrite pipeline that is resilient, observable, and integrates seamlessly with the manual verification gate.

## Phases

### Phase 1: Resilience & Resumption
- [ ] 1.1: Implement `Job_Registry`: Track `batch_id` for AI generation sessions.
- [ ] 1.2: Add "Resume" capability: If `AI_Planner` crashes, the next batch run detects `rewriting` items and continues rather than restarting.
- [ ] 1.3: Enforce Timeouts: Ensure individual item generation has a hard deadline (e.g., 60s) to prevent stalled batches.

### Phase 2: Platform Constraints & Integrity
- [ ] 2.1: Update `Entity_Normalizer` to run *during* the generation phase, not just at posting.
- [ ] 2.2: Implement "Hard Limit" checks: Verify generation length against known platform character limits (e.g., Mastodon 500, X 280) *before* marking as `prepared`.
- [ ] 2.3: Validate output format: Ensure `Gemini` returns valid JSON/expected structure.

### Phase 3: Observability & Feedback
- [ ] 3.1: Dashboard Progress: Add a websocket or polling indicator to `/rewrites` showing "Generation progress: X/Y items".
- [ ] 3.2: Error Aggregation: Surface "Why it failed" directly in the Review UI for failed items.

### Phase 4: Verification & Finality
- [ ] 4.1: Audit Trail: Store a `version_hash` or `generation_metadata` with each rewrite.
- [ ] 4.2: Conflict Resolution: If `source_idea` is edited after rewrite, mark rewrite as `stale` (triggering a visible warning to the user).

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `NameError: RewriteContext` | 1 | Added missing import in `gemini.py` |
