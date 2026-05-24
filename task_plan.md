# Task Plan: M5 — Async Worker System

## Goal
Implement a robust, asynchronous worker runtime that consumes publishing tasks from a queue, handles platform sessions reliably, and ensures structured, observable execution.

## Components
1. **Task Queue (`asyncio.Queue`)**: Centralized job management.
2. **Worker Runtime (`asyncio` loop)**: Manages concurrency and task consumption.
3. **Task Definition**: Structured schema for `PublishTask`.
4. **Session Management**: Persistent browser context handling (leveraging M2/M3 findings).
5. **Scheduler (APScheduler)**: For future-proofing task timing.

## M52 — Critical Review Fix
**Objective**: Remediate architectural risks (platform routing, browser lifecycle).

### Phases
1. [ ] **Foundation**: BrowserProvider Implementation.
2. [ ] **Registry**: Platform Registry & Orchestration.
3. [ ] **Observability**: Error Handling & Artifact Capture.
4. [ ] **Refactor**: Mastodon Handler conversion.
5. [ ] **Verification**: Final Cleanup.
