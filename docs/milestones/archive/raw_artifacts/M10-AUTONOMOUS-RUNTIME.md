# Specification: M10 Autonomous Runtime

## Problem Statement
The current `AsyncIOScheduler` is ephemeral and disconnected from the database state, leading to race conditions where the runtime drift from the actual intent in the UI.

## Requirements
1. **DB-Driven Polling:** Replace the scheduler with a `StatusPoller` in `src/worker.py` that continuously queries the database for `status = 'ready_to_post'`.
2. **Atomic Claiming:** Use SQL updates to claim tasks: `UPDATE content SET status = 'posting', attempt_count = attempt_count + 1, last_attempt_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'ready_to_post'`.
3. **Robust Lifecycle:**
    - Tasks must transition: `ready_to_post` -> `posting` -> (`posted` | `failed`).
    - Failed tasks remain in `failed` state.
4. **Graceful Shutdown:** Implement `SIGTERM` handler to drain current job before exiting.
5. **Retry Tracking:** Add `attempt_count` and `last_attempt_at` to the `content` table.

## Architecture
- **Worker Loop:** Blocking/sequential loop. One task at a time.
- **State Machine:**
    - `ready_to_post`: Waiting for worker.
    - `posting`: Actively being processed.
    - `posted`: Success.
    - `failed`: Terminal failure state (manual reset required).

## Implementation
1. **Migration:** Add `attempt_count` (int) and `last_attempt_at` (timestamp) to `content` table.
2. **Worker:** Implement `StatusPoller` in `src/worker.py`.
3. **Cleanup:** Remove `AsyncIOScheduler` dependencies.

## Acceptance Criteria
- Tasks picked up immediately.
- Zero race conditions.
- Workers exit cleanly on `SIGTERM`.
- Database schema supports tracking.
