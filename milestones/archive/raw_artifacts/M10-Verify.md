# Verification: M10-Verify.md

## Success Conditions
- Workers correctly identify tasks with `status = 'ready_to_post'`.
- Atomic `UPDATE` claims prevent multiple workers from handling the same task (though system scope typically limits concurrent workers).
- Tasks transition correctly: `ready_to_post` -> `posting` -> (`posted` | `failed`).
- Database accurately logs `last_attempt_at` using DB-native `CURRENT_TIMESTAMP`.

## Edge Cases
- **Concurrent DB contention:** Verify atomic claim handles collisions gracefully.
- **Unexpected Crash:** Verify `SIGTERM` handler marks in-flight tasks as `failed` rather than leaving them in `posting` state indefinitely.
- **Transient Failures:** Ensure `attempt_count` increments correctly on failure.

## Failure Conditions
- Worker enters infinite loop on a specific failing task.
- Task remains 'posting' indefinitely after a service restart.
- Database state drifts from worker runtime state.

## Manual Validation Steps
1.  **Seed Database:** Insert records with `status = 'ready_to_post'`.
2.  **Start Worker:** Observe console output for task pickup.
3.  **Signal Testing:** Send `kill -15 [worker_pid]` during execution of a task. Check DB for `failed` status for that record.
4.  **Verification:** Query `content` table to ensure state transition is correct.

## Test Cases
- `test_atomic_claim`: Execute two simultaneous update queries. Assert only one row is affected.
- `test_sigterm_handling`: Trigger `status='posting'`. Send SIGTERM. Verify row state updates to `failed`.
- `test_retry_mechanism`: Simulate task failure. Assert `attempt_count` increased by 1 and state is `failed`.

## Regression Risks
- Existing scheduling logic might interfere if not fully removed.
- Database locks if transactions are poorly scoped.

## Approval Status
Approved
