# Milestone M8: UX Architecture & Domain Extraction

**Status:** PENDING  
**Objective:** Transition the frontend from a monolithic "Phase 1" table to a scalable "Phase 3" Information Architecture designed for an "autonomous media operations system."

## Context & Rationale
As established during the M7 review, the UI is reaching "Operational Collapse." Attempting to force multi-platform AI reviews, error handling, and content management into a single table row violates our goal of building an expert operator UI.

We are shifting from "fewer pages" to "fewer clicks to resolve work".

## New Information Architecture
We will implement a unified layout shell (Sidebar + Main Content) using standard HTML/Jinja2/Tailwind, routing requests via FastAPI.

```txt
Autonomedia
├── Command Center (/)         <- Triage, Inbox, Action Queue, Failures
├── Content (/content)         <- Idea generation, Drafts, Scheduled, Archive
├── AI Review (/review)        <- Full-screen subsystem for diffs, regen, approval
├── Platforms (/platforms)     <- Accounts, auth states, adapters
├── System Logs (/logs)        <- Queue health, rate limits, failures
```

## Execution Steps

### 1. Unified Navigation Shell
*   Create a base Jinja template (`base.html`) with a persistent left sidebar navigation.
*   Update `app.py` routers to support the new endpoints.

### 2. The Command Center (The "Inbox")
*   Refactor the root `/` to only show items requiring human attention:
    *   Items in `prepared` state waiting for AI Review.
    *   Items in `failed` state needing triage.
*   Remove the "Add Content" form from this page.

### 3. Content Domain
*   Move the "Add Content" form and the raw list of `idea` and `published` states to a dedicated `/content` view.
*   Focus this view on backlog management.

### 4. AI Review Subsystem
*   Create a dedicated `/review/{id}` page.
*   This page will feature a split-screen or large-card layout showing the original idea vs the AI outputs for each platform.
*   Include clear "Approve & Queue", "Regenerate", or "Edit" actions.

## Success Criteria
*   The UI has distinct navigation sections.
*   The Command Center acts strictly as a triage inbox (zero scrolling required to see action items).
*   Approving an AI post takes 1 click from the dedicated Review screen.
*   No complex JS frameworks added (HTMX and Tailwind remain the standard).
