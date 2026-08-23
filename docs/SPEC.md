# AUTONOMEDIA — SPEC.md

## PROJECT NAME

Autonomedia

Project path:

```text
~/devcode/autonomedia
````

---

# PROJECT PURPOSE

Autonomedia is a local-first autonomous publishing runtime.

Primary use-case:

* personal brand automation
* referral content distribution
* evergreen content rotation
* browser-first social publishing

Target platforms:

* X
* LinkedIn
* Bluesky
* Mastodon
* Threads
* Facebook Pages

---

# DESIGN PHILOSOPHY

The system should behave like:

* a reliable publishing operator
* a personal media assistant
* an inspectable automation runtime

The system should NOT become:

* AI swarm chaos
* no-code spaghetti
* over-abstracted framework soup

---

# MVP GOALS

## Phase 1

Reliable posting to:

1. Mastodon
2. Bluesky

Requirements:

* persistent browser sessions
* human-like interaction pacing
* verified successful posts
* screenshots
* structured logs
* randomized scheduling
* canonical content storage
* AI rewrite generation

---

# CONTENT MODEL

Canonical posts are approved by human.

Generated variants are ephemeral.

Canonical content includes:

* base text
* links
* tags
* category
* cooldown rules
* allowed platforms

Variants are generated dynamically:

* platform-specific
* timing-specific
* tone-adjusted

---

# BROWSER AUTOMATION POLICY

Browser automation is the primary execution layer.

Reasons:

* platform independence
* future workflow flexibility
* human-like interaction
* avoids API fragmentation
* compatible with future tasks

Examples of future tasks:

* replying
* DMs
* analytics collection
* engagement workflows
* trend scraping

---

# PERSISTENT PROFILE STRATEGY

Each platform receives isolated Chromium profile.

Example:

```text
browser/profiles/
├── x/
├── linkedin/
├── mastodon/
├── bluesky/
├── threads/
└── facebook/
```

Benefits:

* isolated cookies
* lower blast radius
* easier debugging
* independent auth recovery

---

# SCHEDULING STRATEGY

Use randomized scheduling windows.

Example:

```text
09:00–11:00
13:00–16:00
18:00–20:00
```

Reasoning:

* human-like behavior
* avoids robotic timing
* lower automation detection risk

---

# AI REWRITE STRATEGY

AI rewrites are stateless.

Every posting event:

1. fetch canonical content
2. generate platform-specific rewrite
3. publish
4. discard generated variant

Benefits:

* infinite freshness
* smaller database
* easier maintenance
* dynamic adaptation

---

# DASHBOARD SCOPE

The UI acts as an **Autonomous Media Operations System**.

Information Architecture focuses on Domain Extraction (M8):
* **Command Center:** Triage, pending approvals, failed jobs. (Lightweight, action-oriented).
* **Content:** Idea backlogs, draft management.
* **AI Review:** A dedicated workflow screen for diffing, scoring, and regenerating platform-specific content.
* **Platforms:** Session health checks, rules, auth management.
* **Analytics:** Operational feedback, token efficiency, failure rates.

Avoid building:
* A monolithic, infinite-scrolling table of everything.
* A traditional Hootsuite clone.
* Modal-heavy reactive state soup.

---

# PI AGENTIC INTEGRATION

Pi acts as:

* implementation coworker
* operational shell
* debugging assistant
* architecture reviewer
* log analyst

Pi does NOT:

* directly orchestrate runtime
* autonomously mutate architecture
* recursively self-manage

---

# SUCCESS CRITERIA

MVP successful when:

* Mastodon posting stable
* Bluesky posting stable
* sessions persist reliably
* failures observable
* logs inspectable
* rewrites platform-aware
* randomized scheduling functional
- # WEB INFRASTRUCTURE
-
- ## Dashboard Implementation
-
- Health dashboard provides real-time visibility into infrastructure status:
-
- - **Components Monitored:**
-   - Database health
-   - Runtime directory status
-   - Test suite integrity
-   - Source code availability
- - **Access Method:**
-   - URL: `/health` (dashboard page)
-   - API: `GET /api/health` (status JSON)
-   - Authentication: Per-project policy (no hardcoded credentials)
- - **Response Format (API):**
-   ```json
-   {
-     "database": "healthy" | "unhealthy",
-     "runtime": "healthy" | "unhealthy",
-     "tests": "healthy" | "unhealthy",
-     "src": "healthy" | "unhealthy"
-   }
-   ```
-
- ## Web Application Structure
-
- The web application follows these principles:
-
- - **Frameworks:** FastAPI (backend), React (dashboard UI), Jinja2 (fallback templates)
- - **Entry Point:** `src/web/app.py` (main FastAPI application)
- - **Routing:** RESTful with single HTTP method per route
- - **Templates:** `src/web/templates/` directory
- - **Components:** `src/web/ui/` directory for React components
-
- ## Integration Requirements
-
- Web features must:
- 1. Integrate into `src/web/app.py` (NOT standalone server files)
- 2. Use React components for dashboard UI (spec requires this)
- 3. Register routes in app router
- 4. Follow existing domain extraction pattern
- 5. Include tests covering happy path and error cases
