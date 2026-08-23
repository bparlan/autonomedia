# Technical Specification: M11 - Observability & Self-Healing

## Problem Statement
Current execution remains "silent" upon failure, lacking diagnostic artifacts and systemic response mechanisms. Observability gaps lead to resource waste and manual debugging overhead.

## Proposed Changes
- **Observability:** Centralized JSON logging via a custom handler in `src/autonomedia/core/worker.py` that enforces standard schemas (`task_id`, `platform_id`, `retry_count`) for every log record.
- **Self-Healing:** Add `failure_count` (int) and `is_paused` (boolean) columns to the `platforms` table. Implement `ErrorResolver` to interpret exceptions and determine whether a task is retryable or should trigger a circuit-breaking pause.
- **Artifacts:** Implement deterministic path resolution. Files will be saved as `storage/screenshots/{task_id}.png` and `storage/dom/{task_id}.html`, accessible by ID without DB record updates.
- **Circuit Breaker:** If `failure_count` reaches 3, `is_paused` = true. The `StatusPoller` will ignore paused platforms.

## Implementation Plan
1. **Infrastructure:** Update DB schema via a new script `scripts/db/migrate_M11_platform_metadata.py`.
2. **Telemetry:** Inject standard JSON logging in the worker loop.
3. **Diagnostics:** Implement `src/autonomedia/core/error_resolver.py` to classify errors.
4. **Integration:** Update `src/autonomedia/core/worker.py` to capture screenshots/DOM on `Exception` before re-raising or logging.

## Acceptance Criteria
- [ ] Platform metadata tracks failures/pauses correctly.
- [ ] Every task failure generates deterministic artifact files.
- [ ] `ErrorResolver` differentiates transient vs. fatal errors.
- [ ] Worker loop automatically halts tasks for paused platforms.
- [ ] JSON logs are valid and searchable via standard tools.
