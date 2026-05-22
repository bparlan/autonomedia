# Task Plan: M5 — Async Worker System

## Goal
Implement a robust, asynchronous worker runtime that consumes publishing tasks from a queue, handles platform sessions reliably, and ensures structured, observable execution.

## Components
1. **Task Queue (`asyncio.Queue`)**: Centralized job management.
2. **Worker Runtime (`asyncio` loop)**: Manages concurrency and task consumption.
3. **Task Definition**: Structured schema for `PublishTask`.
4. **Session Management**: Persistent browser context handling (leveraging M2/M3 findings).
5. **Scheduler (APScheduler)**: For future-proofing task timing.

## Phases
1. [ ] **Foundation**: Setup `asyncio` task loop and queue structure.
2. [ ] **Task Definition**: Standardize the publishing task schema.
3. [ ] **Worker Logic**: Migrate the "post" logic into a reusable worker function.
4. [ ] **Observability**: Integrate structured JSON logging into the worker loop.
5. [ ] **Verification**: Add retries and error handling for failed tasks.
