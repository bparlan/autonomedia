# Milestone M11: Observability & Self-Healing

**Status:** PENDING
**Objective:** Build a feedback loop that transforms the system into an "inspectable" operator.

## Context & Rationale
Automation is useless without observability. We need to catch failures when they happen and enable the UI to display exactly why a task failed, with artifacts ready for review.

## Execution Steps

### 1. Structured Telemetry
*   Refactor `logger.info` calls in `worker.py` to stream standard JSON logs to `storage/logs/worker.json`.

### 2. Failure Triage Engine
*   Create a `/logs` dashboard.
*   Parse `error_log` from the `content` table to display human-readable errors (e.g., "Authentication Required" vs "Rate Limited").

### 3. Automated Artifacts
*   Update `execute_task` exception block:
    *   `page.screenshot()` → `storage/screenshots/{task_id}.png`
    *   `page.content()` → `storage/dom/{task_id}.html`
    *   Update DB with these paths.

### 4. Self-Healing
*   Implement tiered retry logic:
    *   Transient errors (Retriable) → Exponential backoff.
    *   Fatal errors (Authentication) → Pause platform queue + Notify UI.

## Success Criteria
*   Errors are not "silent"; every failure has a screenshot and DOM capture.
*   System automatically pauses a platform queue if 3 consecutive failures occur, preventing log spam and resource waste.
