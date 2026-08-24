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

# MVP GOALS: IDEA FEATURE (MILESTONE 0)

Our initial MVP focuses on the "Idea" feature, enabling solo developers to define and automate content distribution.

## Phase 1: Core Idea Scheduling & Mastodon Publishing

*   **Goal:** Reliable posting of AI-rewritten "Ideas" to Mastodon.
*   **Key Functionality:**
    1.  User defines an "Idea" with content, schedule, AI styles, and target platform (Mastodon).
    2.  System automatically generates unique content variants for each scheduled post using AI.
    3.  Validated content is published to Mastodon on schedule.

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

---

# IDEA FEATURE (RE-POSTING & AI AUTOMATION)

The "Idea" is the core entity for long-term content distribution. Unlike a single post, an Idea is a persistent campaign that generates multiple unique posts over time.

## Core Concept
* **Longevity:** User defines an Idea with a duration (e.g., 1 month).
* **Diversity:** AI rewrites the Idea for each scheduled slot so no two posts are identical.
* **Consistency:** Adheres to a predetermined "Whitelist Contact Truth Registry" for handles, hashtags, and links.

## Data Fields
| Field | Description |
|-------|-------------|
| Title | Internal name for the campaign. |
| Base Content | The core message/facts to be shared. |
| Referral Link | Canonical link to be included in posts. |
| Tags | Hashtags or categories for tracking. |
| Whitelist Contacts | Predetermined handles to be tagged/mentioned. |
| Duration | Time period for the campaign (relative to start). |
| Frequency | How often to post (e.g., every 3 days, once a week). |
| Platform List | Target social networks (MVP: Mastodon). |
| AI Style Presets | Instructions for AI tone (punchy, professional, etc.). |

## Workflow
1. **Creation:** User creates an Idea via the "Content" domain UI.
2. **Scheduling:** The system computes the sequence of post dates based on duration and frequency.
3. **Generation:** For each date, the AI Rewrite module generates a new variant based on "Base Content" and "Style Presets".
4. **Validation:** Rewrites are checked against the Whitelist Registry for handle/link accuracy.
5. **Posting:** The Platform Adapter (Mastodon) executes the post.
6. **Analytics:** Performance is aggregated at the Idea level (total reach, clicks across all variants).


# AI REWRITE STRATEGY

AI rewrites are stateless, ensuring content freshness and adaptability. Each posting event dynamically generates a unique content variant.

## Workflow for Each Scheduled Post:

1.  **Fetch Idea Context:** Retrieve the `Idea` record, including `Base Content`, `AI Style Presets`, `Referral Link`, `Tags`, and `Whitelist Contacts`.
2.  **Generate Platform-Specific Rewrite:** Invoke the AI Rewrite module to create a new content variant, adhering to `AI Style Presets` and platform constraints.
3.  **Validate Content:** Verify the rewritten content against the `Whitelist Contact Truth Registry` for handles, hashtags, and referral links.
4.  **Publish:** Post the validated, rewritten content to the designated platform (e.g., Mastodon).
5.  **Discard Variant:** The ephemeral generated variant is discarded post-publication.
Benefits:

* infinite freshness
* smaller database
* easier maintenance
* dynamic adaptation

---


---

## Whitelist Contact Truth Registry

The authoritative list of safe handles, hashtags, and links is stored in `src/autonomedia/content/mention_registry.json`.

* **Validation Rule:** AI-generated rewrites must be parsed and verified against this registry before being marked as `ready_to_post`.
* **Safety:** Prevents AI from hallucinating incorrect handles or links.

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

# SUCCESS CRITERIA (MILESTONE 0 - MVP)

The MVP is successful when a solo developer can reliably:

*   Create and manage "Ideas" through the UI.
*   See AI-rewritten content variants published automatically to Mastodon.
*   Observe scheduled posts occurring at the defined frequency.
*   Confirm that generated content adheres to specified `AI Style Presets`.
*   Verify that `Whitelist Contacts` and `Referral Links` are correctly included in posts.
*   Inspect logs to understand the publishing workflow and identify any failures.
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
