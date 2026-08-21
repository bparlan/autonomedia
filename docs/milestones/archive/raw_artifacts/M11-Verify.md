# Verification: M11-Observability-Self-Healing

## Success Conditions
- [ ] Database Schema: `platforms` table includes `failure_count` (int) and `is_paused` (bool).
- [ ] JSON Logs: Every task emits logs with `task_id`, `platform_id`, and `retry_count`.
- [ ] Artifacts: On any exception, `storage/screenshots/{task_id}.png` and `storage/dom/{task_id}.html` are created deterministically.
- [ ] Circuit Breaker: `failure_count` == 3 automatically sets `is_paused` = true.
- [ ] Worker: `StatusPoller` correctly skips platforms where `is_paused` = true.

## Edge Cases
- **Storage Pressure:** High task failure rates will fill disk space. Current strategy is "monitor and audit", with a pending ticket for an automated TTL cleanup policy.
- **Concurrent Updates:** Two tasks hitting the failure threshold simultaneously could trigger race conditions. Optimistic locking is sufficient given current traffic.

## Failure Conditions
- **Persistence Failure:** DB write fails during `failure_count` update; system should re-raise the application exception (Worker safety).
- **Resolver Failure:** `ErrorResolver` encounters an unknown exception type; default behavior must be "Treat as fatal to prevent infinite loops".

## Manual Validation Steps
1. **Unpausing:** Use `scripts/checks/unpause_platform.py <platform_id>` to reset `failure_count` to 0 and `is_paused` to false. 
2. **Artifact Verification:** Simulate a failure using `FaultInjector`, check `storage/` for presence of `task_{id}.png` and `task_{id}.html`.

## Test Cases
- `test_error_resolver_classifies_transient_vs_fatal`: Unit test.
- `test_circuit_breaker_halts_paused_platform`: Integration test using `FaultInjector`.
- `test_artifact_generation_triggered_on_exception`: Integration test.

## Regression Risks
- Artifact accumulation (cleanup policy pending).
- Risk of false-positive pauses due to incorrect Exception classification.
