# Verification: M10 Autonomous Runtime

## Success Conditions
1. **FIFO Processing**: Tasks are claimed in order of `created_at` (ascending).
2. **Atomic Claim**: The `UPDATE` query correctly claims exactly one task per request.
3. **State Transitions**:
    - `ready_to_post` -> `posting` (on pick up).
    - `posting` -> `posted` (on success).
    - `posting` -> `failed` (on error).
4. **Shutdown Rollback**: If `SIGTERM` is received while a task is in `posting`, it is rolled back to `ready_to_post` to avoid orphans.
5. **Retry Tracking**: `attempt_count` increments on every pick up.

## Edge Cases
1. Worker interrupted during `posting` state (SIGTERM).
2. Empty queue processing.
3. Multiple attempts on a task (increments `attempt_count`).

## Failure Conditions
1. Task lost during shutdown (orphan `posting` state).
2. Task picked up out of chronological order.
3. `attempt_count` fails to increment.

## Manual Validation Steps
1. Insert multiple `ready_to_post` tasks into DB.
2. Trigger worker with mocked `SIGTERM` while processing.
3. Verify task returns to `ready_to_post`.
4. Run standard worker flow and verify transition to `posted`.

## Test Cases
1. `test_fifo_ordering`: Verify claim order.
2. `test_lifecycle_transition`: Verify state machine.
3. `test_shutdown_rollback`: Verify SIGTERM returns task to ready state.
4. `test_retry_increment`: Verify attempt_count logic.

## Regression Risks
- Existing database constraints on `content` table.
- Interaction with `platform_health` table.

## Approval Status
Draft
