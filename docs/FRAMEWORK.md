# AUTONOMEDIA - FRAMEWORK.md

## System Architecture Overview

Autonomedia is designed as a local-first, modular autonomous publishing runtime, empowering solo creators to manage and distribute their "Ideas" across social platforms. It prioritizes user control, inspectability, and intelligent automation.

### Core Architectural Principles
1.  **Local-First Autonomous Runtime:** Operates on the user's machine for direct control and offline capability.
2.  **Modular & Extensible:** Components (schedulers, AI, platform adapters) are independently replaceable and extendable.
3.  **Browser-First Interaction:** Employs Playwright for human-like web interactions, ensuring platform independence.
4.  **Async-Native:** Built for non-blocking I/O and efficient task handling, supporting scalability.
5.  **Deterministic Outputs:** Aims for predictable results in content generation and scheduling.

### System Map Links

-   **Data Flow Diagram:** [Data Flow](xref:docs/system_map_data_flow.md)
-   **UI Flow:** [Content Creator Journey](xref:docs/system_map_ui_flow.md)
-   **Interaction Matrix:** [Component Interactions](xref:docs/system_map_interaction_matrix.md)


# TECHNOLOGY STACK

## Language

Python 3.12+

Reasoning:
- mature Playwright ecosystem
- async ecosystem strong
- AI integrations trivial
- good tooling
- compatible with pi workflows


## Platform Integration Strategy

-   **Modular Adapters:** Each social platform is integrated via a dedicated `Platform Adapter` (e.g., MastodonTaskHandler) in `src/autonomedia/platforms/`. These adapters encapsulate platform-specific logic, API interactions, and authentication.
-   **Content Adaptation:** As part of Milestone 1 (Multi-Platform Expansion), content will be dynamically adapted for platform-specific constraints (character limits, media types) and tone guidelines (professional for LinkedIn, punchy for X, community-focused for Mastodon). This ensures optimal presentation across diverse networks.


# PACKAGE MANAGEMENT

Use uv.

Never use:
- pip directly
- poetry initially

Reasoning:
- faster
- cleaner dependency resolution
- modern workflow
- reproducible environments

Installation:

```bash
brew install uv
````

Project init:

```bash
mkdir -p ~/devcode/autonomedia
cd ~/devcode/autonomedia
uv init
```

---

# CORE DEPENDENCIES

```bash
uv add playwright
uv add sqlalchemy
uv add asyncpg
uv add pydantic
uv add fastapi
uv add uvicorn
uv add structlog
uv add google-genai
uv add python-dotenv
```

Install browser:

```bash
playwright install chromium
```

---

# TEMPLATE EDGE CASE HANDLING

## Content & Idea Verification Status Synchronization

-   The system generates and manages content variants for `Ideas`. These variants require verification (e.g., against the Whitelist Contact Truth Registry) before posting.
-   Templates responsible for displaying content status MUST gracefully handle missing or pending verification statuses for `Ideas` and their generated posts.
-   Never assume verification status completeness; always check for key existence (e.g., `idea.posts.verification_status`).

### Concurrent Scheduling & Approval Safety

When processing or approving `Idea` posts concurrently, use robust mechanisms (like database-level row locking) to prevent race conditions. Two simultaneous requests could both pass a status check before either writes, leading to duplicate posting attempts or inconsistent schedules. Always wrap concurrent status checks and updates in transaction isolation or use `FOR UPDATE` for PostgreSQL-level locking.

### Optimized Status Building

Building verification and scheduling statuses for `Ideas` and their associated posts should be consolidated into a single-pass logic flow. Avoid separate filtering and status checks, as this increases maintenance burden and potential for divergence. Integrate status building inline during `Idea` and post iteration.

# ASYNC DESIGN EXPLANATION

## Why Async?

Browser automation spends most time waiting:

* pages loading
* selectors appearing
* network responses
* AI requests
* queue events

This is IO-bound work.

Async allows:

* one runtime handling many operations efficiently
* future concurrency
* scalable scheduling
* lower resource waste

Example:

Without async:

```text
wait browser
wait network
wait AI
wait queue
```

With async:

```text
multiple tasks progress simultaneously
```

This becomes critical later for:

* client accounts
* multiple workers
* analytics jobs
* background rewriting

---

# PLAYWRIGHT PHILOSOPHY

## Accessibility-First Selectors

Playwright excels at semantic selectors.

Preferred APIs:

```python
page.get_by_role()
page.get_by_label()
page.get_by_text()
```

Advantages:

* resilient to redesigns
* aligned with accessibility metadata
* easier debugging
* more readable automation

Example:

Bad:

```python
page.locator("div > div:nth-child(4) button")
```

Good:

```python
page.get_by_role("button", name="Post")
```

## PLAYWRIGHT POLICY

Prefer accessibility selectors. Violations are architectural debt.

```python
page.get_by_role("button", name="Post")   # correct
page.locator("div:nth-child(5) > span > button")  # never
```

Use: `get_by_role()`, `get_by_label()`, `get_by_text()`
Avoid: CSS chains, nth-child, fragile DOM traversal.

---

# DATABASE

Autonomedia supports both SQLite for local development and PostgreSQL for production deployments.

-   **Local Development:** SQLite (via `src/autonomedia/database/client.py`) provides a lightweight, file-based database ideal for solo developer workflows and rapid prototyping.
-   **Production:** PostgreSQL is the recommended database for production environments due to its robustness, scalability, and advanced features.

Postgres should become source-of-truth immediately for multi-user/scaled deployments.

Google Sheets only acts as ingestion source.

For detailed schema definitions, table structures, and ingestion strategies, see [DATA.md](./DATA.md).
# LOCAL PROCESS PHILOSOPHY

# LOCAL PROCESS PHILOSOPHY

Use native local runtime.

Avoid Docker initially.

Reasoning:

* browser automation simpler
* macOS compatibility easier
* lower debugging complexity
* persistent profiles easier

Recommended local tooling:

* uv
* tmux
* launchd
* native processes

---

# LOGGING STACK

Use structlog.

All logs JSON structured.

Reason:

* machine readable
* pi-compatible
* searchable
* future analytics friendly

---

# BROWSER PROFILE MANAGEMENT

Each platform has isolated profile, selectors, posting logic, validation. No universal adapter.

Profiles stored under:

```text
browser/profiles/
```

Never share browser state across platforms.

---

# FUTURE STACK EXPANSIONS

Planned future capabilities, aligned with the phased roadmap:

-   **Milestone 1 (Multi-Platform Expansion):** Enhanced client account isolation, multi-platform support.
-   **Milestone 2 (Advanced AI & Content Control):** Semantic memory, analytics intelligence, advanced knowledge retrieval for AI.
-   **Milestone 3 (Analytics, Monitoring & Refinement):** Comprehensive analytics intelligence and advanced monitoring capabilities.
-   **Milestone 4 (Extensibility & Future Growth):** Plugin architecture for new capabilities and agent-to-agent collaboration.

Current architecture must preserve compatibility with these future developments.
---

# PIPELINE INTEGRITY RULE: EXPLICIT DISPATCH

Async workers in a modular pipeline MUST explicitly invoke downstream handlers. Database status updates alone do NOT constitute execution. Any async queue processor that lacks a dispatch block (e.g., calling `publish_mastodon`, `execute_x`, etc.) will silently succeed on schema changes but never achieve the business goal. Future implementations of `PostingSecretary` or similar workers MUST include a dispatch phase before concluding with status updates.

---

# UX ARCHITECTURE

We build an "autonomous media operations system" with a user-centric design, not a basic web app. The UI provides a clear, actionable overview of `Idea` campaigns and system health.

## UI Framework Strategy

Autonomedia employs a hybrid UI framework strategy:

-   **FastAPI & Jinja2:** For simpler, server-rendered pages and foundational UI elements.
-   **React (for Dashboards):** For complex, interactive dashboards and dynamic data visualization (e.g., advanced analytics, real-time status updates, intricate `Idea` management interfaces).

Constraints:
-   Prioritize "Fewer clicks to resolve work" over "Fewer pages."
-   Utilize "Phase 3 Domain Extraction" for logical grouping of functionality.

Domains:
-   **Command Center:** Operational overview, triage, action queue (pending approvals, failures related to `Ideas`).
-   **Content:** Dedicated backlog and `Idea` management, creation, and editing.
-   **AI Review:** First-class subsystem for inspecting AI-generated diffs, regenerating variants, and approving `Idea` output.
-   **Platforms:** Dedicated integration health (session cookies, auth limits for platform adapters).
-   **Analytics:** Dedicated feedback layer for `Idea` performance and system health.


# PROJECT LAYOUT

```
autonomedia/
├── docs/                    # Canonical documentation
│   ├── CHANGELOG.md        # Version history
│   ├── DATA.md             # DB schema & storage
│   ├── FRAMEWORK.md        # Design principles & stack rules
│   ├── MILESTONES.md       # Milestone objectives & history
│   ├── PLAYBOOK.md         # Operator guide & failure modes
│   ├── ROADMAP.md          # Vision & strategic alignment
│   ├── SPEC.md             # Functional requirements
│   ├── system_map_data_flow.md   # Data flow diagram
│   ├── system_map_interaction_matrix.md   # Component interaction matrix
│   ├── system_map_inventory.md   # UI template & route inventory
│   └── system_map_ui_flow.md   # Content Creator UI flow
├── runtime/                 # Ephemeral state (browser profiles, sessions, temporary files)
│   ├── browser_profiles/
│   ├── sessions/
│   └── tmp/
├── scripts/                 # Utility scripts
│   ├── checks/             # Diagnostics & platform verifications
│   └── db/                 # Migrations & schema updates
├── src/                     # Application code
│   ├── autonomedia/
│   │   ├── ai/             # AI-related modules
│   │   │   ├── rewriting/  # Content rewriting (base, gemini.py)
│   │   │   └── ...
│   │   ├── api/            # API endpoints (health.py, router.py)
│   │   ├── core/           # Core business logic (scheduler.py, posting_routine.py, worker.py, logger.py, security.py, error_resolver.py, poller.py, verification.py, config/, db/, observability/, analytics/)
│   │   │   └── scheduler.py # Idea scheduling engine
│   │   ├── content/        # Content-related modules
│   │   │   ├── ingestion/  # Content ingestor
│   │   │   └── mention_registry.json # Whitelist Contact Truth Registry
│   │   ├── database/       # Database client and schema (client.py, schema.py)
│   │   ├── platforms/      # Platform-specific adapters (mastodon/, linkedin/, x/, ...)
│   │   │   └── mastodon/   # Mastodon platform handler (task_handler.py, post_handler.py)
│   │   └── web/            # Web application components
│   │       ├── main.py     # Main FastAPI app entry point
│   │       ├── router.py   # Web router
│   │       ├── models.py   # Pydantic/SQLAlchemy models
│   │       ├── templates/  # Jinja2 templates (health.html, dashboard.html, etc.)
│   │       └── ui/         # React components (e.g., health.jsx)
│   └── ...
├── storage/                 # Persistent outputs (logs, screenshots, exports)
├── tests/                   # Unit, integration, and e2e tests
│   └── M0/                 # Tests for Milestone 0
└── pyproject.toml           # Project metadata and dependencies (uv)
```
# PROJECT LAYOUT

```
autonomedia/
├── docs/                    # Canonical documentation
│   ├── CHANGELOG.md        # Version history
│   ├── DATA.md             # Database schema and ingestion strategy
│   ├── FRAMEWORK.md        # Technology stack and architectural patterns
│   ├── MILESTONES.md       # Milestone tracking and lifecycle
│   ├── PLAYBOOK.md         # Operational procedures and failure modes
│   ├── ROADMAP.md          # Project vision and phases
│   ├── RUNTIME.md          # Execution model and observability
│   ├── SPEC.md             # System architecture and APIs
│   ├── AI_FLOW.md          # AI rewrite pipeline documentation
│   └── STRUCTURE.md        # This file
├── runtime/                # Ephemeral runtime state
│   ├── browser_profiles/   # Chromium profiles (auto-generated)
│   ├── sessions/           # Active session data
│   └── tmp/                # Temporary files
├── scripts/                # Operational scripts
│   ├── checks/             # Health checks and diagnostics
│   │   ├── check_health.py
│   │   ├── check_platforms.py
│   │   ├── check_status.py
│   │   ├── verify_health.py
│   │   ├── verify_telegram.py
│   │   ├── check_all_platforms.py
│   │   ├── check_data.py
│   │   └── check_db.py
│   ├── db/                 # Database migrations and updates
│   │   ├── migrate_db.py
│   │   ├── migrate_m10.py
│   │   ├── migrate_m11.py
│   │   ├── migrate_m12.py
│   │   ├── migrate_m13.py
│   │   ├── migrate_db.py
│   │   └── verify_db.py
│   └── [other scripts]     # Ingestion, content management, etc.
├── storage/                # Persistent outputs
│   ├── logs/               # Runtime logs
│   ├── screenshots/        # Browser screenshots
│   └── exports/            # Published content exports
├── src/                    # Application code
│   ├── autonomedia/
│   │   ├── agents/         # AI agents
│   │   │   └── posting_secretary/
│   │   ├── ai/             # AI modules
│   │   │   ├── analysis.py
│   │   │   ├── planner.py
│   │   │   └── rewriting/
│   │   │       ├── base.py
│   │   │       ├── context.py
│   │   │       ├── gemini.py
│   │   │       └── __init__.py
│   │   ├── apps/           # Application entry points
│   │   │   └── worker/
│   │   ├── content/        # Content processing
│   │   │   └── transforms/
│   │   ├── core/           # Core infrastructure
│   │   │   ├── config/
│   │   │   ├── db/
│   │   │   ├── observability/
│   │   │   │   ├── monitor.py
│   │   │   │   └── telegram.py
│   │   │   ├── storage/
│   │   │   │   └── analysis_storage.py
│   │   │   ├── utils/
│   │   │   │   └── verification.py
│   │   │   ├── worker.py
│   │   │   ├── logger.py
│   │   │   ├── posting_routine.py
│   │   │   ├── security.py
│   │   │   ├── error_resolver.py
│   │   │   └── poller.py
│   │   ├── database/       # Database layer
│   │   │   ├── client.py
│   │   │   └── schema.py
│   │   ├── ingestion/      # Content ingestion
│   │   │   └── content_ingestor.py
│   │   ├── platforms/      # Platform-specific handlers
│   │   │   └── mastodon/
│   │   │       └── task_handler.py
│   │   └── web/            # Web application
│   │       ├── main.py
│   │       ├── models.py
│   │       └── api/
│   │           ├── comments.py
│   │           ├── content.py
│   │           └── likes.py
│   ├── tests/              # Test suites
│   │   ├── ai/
│   │   ├── e2e/
│   │   ├── fixtures/
│   │   │   └── rewrite/
│   │   ├── integration/
│   │   ├── unit/
│   │   └── [test files]
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── content.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── partials/
│   │   │   ├── content_edit_form.html
│   │   │   ├── content_row.html
│   │   │   ├── edit_form.html
│   │   │   └── review_form.html
│   │   ├── registry.html
│   │   ├── review.html
│   │   └── rewrites.html
│   └── web/                # Web app entry
│       └── app.py
├── .venv/                  # Python virtual environment (auto-generated)
├── .gitignore
├── .pre-commit-config.yaml
├── justfile                 # Convenience commands
├── pyproject.toml          # Project manifest and dependencies
├── pytest.ini              # Test configuration
└── README.md               # Project overview

Milestone artifacts in docs/milestones/
├── archive/                 # Completed milestones (M1-M14)
│   ├── raw_artifacts/       # Test outputs and verification logs
│   ├── M1_Content_Idea_Ingestion_AI_Analysis.md
│   ├── M5B.md
│   ├── M5C.md
│   ├── M5X.md
│   ├── M6.md
│   ├── M7.md
│   ├── M8-M11-Archive.md
│   ├── M12.md
│   ├── M12-findings.md
│   ├── M13*.md (all variants)
│   ├── M14.md
│   └── [other artifacts]
├── specs/                   # Active milestone specifications
│   └── M14S1.md
├── verifications/           # Active verification documents
│   └── M14S1V.md
└── reviews/                 # Active review documents
    └── M14S1R.md

Test suites
├── conftest.py              # Pytest configuration
├── run_scenarios.py         # Scenario-based tests
├── simple_test.py
├── [test_m*.py files]       # Milestone-specific tests
└── [test_*.py files]        # Module-specific tests
```
- ---
- # WEB APPLICATION ARCHITECTURE
-
- ### Entry Point
-
- Primary FastAPI application entry point: `src/web/app.py`
-
- This app serves the main Autonomedia web interface with the following domains:
- - **Command Center:** Operational overview, triage, action queue
- - **Content:** Idea backlogs, draft management
- - **AI Review:** AI diff inspection and content regeneration
- - **Platforms:** Platform-specific verification and status
- - **Analytics:** Operational feedback and metrics
-
- ### Dashboard Implementation
-
- Health dashboard for infrastructure monitoring:
- - **Location:** `src/autonomedia/web/ui/dashboard/health.jsx` (React component)
- - **Template:** `src/autonomedia/web/templates/health.html` (fallback)
- - **API Endpoint:** `GET /api/health` (requires implementation integration)
- - **Integration:** Must be integrated into `src/web/app.py` router
-
- ### Routing Pattern
-
- All web routes follow this pattern:
- 1. Domain extraction (per UX architecture)
- 2. Single HTTP method per route (GET/POST only)
- 3. Template-based rendering for HTML responses
- 4. JSON responses for API endpoints
-
- ### React vs Templates
-
- **Preferred:** React components for complex, interactive UI
- - Better state management
- - Easier testing
- - More maintainable
-
- **Fallback:** Jinja2 templates (current implementation)
- - Faster to implement
- - No build step required
- - Good for simple pages
-
- ### Router Hierarchy
-
- ```
- src/web/app.py (Main entry point)
- ├── / (Root)
- ├── /content (Content management)
- ├── /platforms (Platform status)
- ├── /rewrites (AI rewrite management)
- ├── /registry (Registry management)
- ├── /health (Health dashboard)
- └── /api/* (API endpoints)
-
- src/autonomedia/web/api/* (API routers)
- ├── comments.py
- ├── content.py
- └── likes.py
- ```
-
- ### Integration Rules
-
- **NEW implementation MUST:**
- - Integrate into `src/web/app.py` (NOT standalone server files)
- - Use React components for dashboard UI (spec requires this)
- - Register routes in app router
- - Follow existing domain extraction pattern
-
- **DO NOT:**
- - Create separate FastAPI apps without clear justification
- - Implement routes in inactive server files
- - Use hardcoded HTML when React component is available
- - Duplicate functionality between files
# DIRECTORY ROLES

## docs/
Canonical documentation layer. All project knowledge lives here.

- **MILESTONES.md**: Tracks all milestones with lifecycle status
- **SPEC.md**: System architecture and public APIs
- **FRAMEWORK.md**: Technology choices and architectural patterns
- **PLAYBOOK.md**: Operational procedures and failure mode handling
- **RUNTIME.md**: Execution model and observability patterns
- **DATA.md**: Database schema and data flow
- **ROADMAP.md**: Project vision and phased roadmap
- **AI_FLOW.md**: AI rewrite pipeline documentation
- **CHANGELOG.md**: Version history and changes

## runtime/
Ephemeral state - not committed to git.

- **browser_profiles/**: Chromium profiles for each platform
- **sessions/**: Active browser sessions
- **tmp/**: Temporary files

## scripts/
Operational scripts for maintenance and diagnostics.

- **checks/**: Health checks and status monitoring
- **db/**: Migrations, updates, and verification utilities

## src/
Application source code.

- **autonomedia/**: Main package
  - **core/**: Core infrastructure (workers, logging, DB, observability)
  - **agents/**: AI agents (PostingSecretary)
  - **ai/**: AI modules (planner, analysis, rewriting)
  - **apps/**: Application entry points (worker)
  - **content/**: Content processing (transforms)
  - **database/**: Database layer (client, schema)
  - **ingestion/**: Content ingestion
  - **platforms/**: Platform-specific handlers
  - **web/**: Web application (API, templates)

## tests/
Test suites organized by type.

## storage/
Persistent outputs - committed to git.

- **logs/**: Runtime logs
- **screenshots/**: Browser screenshots
- **exports/**: Published content exports

# MILESTONE LIFECYCLE

1. **Proposal**: Milestone documented in `specs/` directory
2. **Implementation**: Code and tests added per specification
3. **Verification**: Verification document created in `verifications/` directory
4. **Review**: Review document created in `reviews/` directory
5. **Approval**: Milestone approved by team
6. **Completion**: All requirements verified, code merged
7. **Archival**: Moved to `docs/milestones/archive/` with full documentation

# CONFIGURATION

- **pyproject.toml**: Project metadata, dependencies, build config
- **pytest.ini**: Pytest configuration
- **.pre-commit-config.yaml**: Git hooks configuration
- **justfile**: Convenience commands for common tasks

# DEPENDENCY MANAGEMENT

- **Package manager**: `uv` (never pip or poetry)
- **Dependencies**: Declared in `pyproject.toml`
- **Virtual environment**: `.venv/` (managed by uv)

# EXECUTION MODEL

## Async-First Runtime

Asyncio throughout. No synchronous blocking.

Main components:
- scheduler
- queue
- workers
- browser sessions
- AI rewrite layer
- analytics logger

## Batch Execution

Currently handled via background task (`asyncio.create_task`), but lacks atomic `batch_id` tracking. If a process interrupts, existing `rewriting` statuses are picked up on restart (potentially duplicating work if not idempotent).

## Error Resolution

`worker.py` utilizes `ErrorResolver.classify()`.

- **Transient**: Triggers auto-retry.
- **Fatal**: Immediately halts, updating status to `failed` to prevent infinite loops.

## High-Level Flow

```text
Dashboard (User adds Idea)
→ Idea saved to DB (status: 'idea')
→ User approves Idea (status: 'approved')
→ PostingSecretary (Worker) polls 'approved'
→ Secretary generates AI rewrites per platform
→ Secretary validates content via ModerationAdapter
→ Content staged in DB (status: 'prepared')
→ Dashboard (User reviews AI output)
→ User approves specific platform variants (status: 'ready_to_post')
→ PostingExecutor (Worker) polls 'ready_to_post'
→ Executor verifies post_history to prevent duplicates
→ Executor executes browser automation
→ Executor verifies successful post
→ Saves logs/screenshots
→ Promotes content to 'published'
```

---

# LOGGING POLICY

Structured JSON. Required fields:
- `timestamp`, `platform`, `task_id`, `worker_id`, `status`, `duration`, `screenshot_path`, `retry_count`, `error_metadata`

---

# BROWSER EXECUTION FLOW

```text
load persistent profile
→ validate auth state
→ open composer
→ inject rewritten content
→ submit
→ verify visible post
→ capture screenshot
→ log success/failure
```

---

# HUMAN-LIKE EXECUTION RULES

Required:

- randomized delays
- pacing jitter
- realistic timing
- avoid robotic execution

Avoid:

- instant interactions
- burst posting
- identical timing

---

# FAILURE POLICY

- Failed post: capture screenshot, logs, DOM snapshot.
- Successful post: capture final screenshot, URL, timestamp.

### Excluded Platform Audit Trail

When platforms are excluded during queue processing, log the exclusion with sufficient context for later auditing. This prevents silent data loss and supports debugging of approval workflow issues.

---

# SESSION RECOVERY

If auth invalid:

- pause posting
- notify operator
- require manual recovery

Avoid automatic re-login systems initially.

---

# PI OPERATIONAL ROLE
- modular services
