# Milestone M10: Autonomous Worker Runtime

**Status:** PENDING
**Objective:** Transition the worker from "hardcoded scheduler" to a "database-driven executor" that enforces the state machine.

## Context & Rationale
Currently, the worker relies on an `AsyncIOScheduler` which is non-persistent and disconnected from the UI's state transitions. We must move to a reactive, DB-driven loop where the database is the source of truth for all jobs.

## Execution Steps

### 1. DB-Driven Polling
*   Remove `AsyncIOScheduler`.
*   Implement a `StatusPoller` in `worker.py` that queries the `content` table for tasks where `status = 'ready_to_post'`.

### 2. State Lifecycle Enforcement
*   Implement atomic "Claim" mechanism using SQL: `UPDATE content SET status = 'posting' WHERE id = ? AND status = 'ready_to_post' RETURNING *`.
*   Ensure that only one worker can claim a task.

### 3. Graceful Shutdown
*   Implement a signal handler for `SIGTERM`.
*   When triggered, prevent new jobs from starting, allow current job to finish, then terminate process.

## Success Criteria
*   Tasks are picked up immediately after they are marked `ready_to_post` in the UI.
*   Zero race conditions (tasks are never duplicated).
*   Workers cleanly exit without hanging tasks.
