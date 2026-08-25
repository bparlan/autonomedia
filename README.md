# Autonomedia | Autonomous Social Media Infrastructure

_Independent Open-Source Project · 2026 – present_

Building an agent-assisted infrastructure for maintaining an autonomous digital presence while preserving platform-specific constraints and human authorship.

---

### Proven Capabilities

- Developed an MVP capable of preparing and publishing social media content without triggering conventional AI-content detection mechanisms through persistent browser profiles, accessibility-first interaction, and human-like pacing.
- Built an agentic rewriting pipeline that preserves protected platform-specific variables including hashtags, mentions, and reference links using a strict Whitelist Contact Truth Registry.
- Designed the system around automated idea intake, transformation into ephemeral variants, and eventual scheduled multi-platform publishing.
- Uses **AEF/SDD** (Agent Execution Framework / Spec-Driven Development) as the engineering framework for managing the project's growing complexity.

> **Why AEF/SDD?**  
> AEF/SDD was not built as a theoretical exercise. It became necessary because Autonomedia reached a level of architectural complexity—combining async queue workers, browser automation, persistent sessions, multi-platform adaptations, and AI moderation—that exceeded the capacity of traditional ad-hoc workflows.

---

> [!WARNING] Under Active Development
> Autonomedia is an experimental, local-first autonomous runtime. APIs, internal schemas, browser selectors, and platform adapters are evolving. Use in production environments with appropriate supervision.

---

## Architecture

Autonomedia is architected as an async-native, modular publishing runtime. It separates content lifecycle management into a state-driven assembly line, decoupled AI rewriting workers, isolated browser automation handlers, and real-time observability.

```text
                                  +------------------------------------+
                                  |     Whitelist Mention Registry     |
                                  |     (mention_registry.json)        |
                                  +-----------------+------------------+
                                                    |
+-------------------+      +------------------------v------------------+      +-------------------+
|   Dashboard UI    | ---> |           State-Driven Assembly Line      | ---> |   PostgreSQL /    |
| (FastAPI / HTMX)  |      | (idea -> approved -> prepared -> ready)   |      |      SQLite       |
+-------------------+      +------------------------+------------------+      +-------------------+
                                                    |
                                  +-----------------+------------------+
                                  |  PostingSecretary (AI Worker)      |
                                  |  - Gemini Rewrite Engine           |
                                  |  - Whitelist Validator             |
                                  +-----------------+------------------+
                                                    |
                                  +-----------------v------------------+
                                  |  PostingExecutor (Browser Worker)  |
                                  |  - Playwright Chromium Profiles    |
                                  |  - Anti-Detection Pacing / Delay   |
                                  +-----------------+------------------+
                                                    |
                                  +-----------------v------------------+
                                  |  Platform Adapters                 |
                                  |  [ Mastodon | LinkedIn | X ]       |
                                  +------------------------------------+
```

### State-Driven Assembly Line

Content moves through a deterministic sequence of state transitions:

1. **`idea`**: Raw concept, canonical base text, schedule parameters, and platform targets created via UI or ingestion.
2. **`approved`**: Idea marked by human operator as eligible for scheduled rewrite generation.
3. **`prepared`**: `PostingSecretary` polls `approved` ideas, executes AI rewriting via Gemini, validates references against `mention_registry.json`, and stages platform variants.
4. **`ready_to_post`**: Ephemeral variants pass moderation checks and wait for the randomized scheduling window.
5. **`published`**: `PostingExecutor` executes browser-native posting, verifies visible publication, captures screenshots, and records immutable history in `post_history`.
6. **`failed`**: Execution errors or verification breaches transition the job to triage status with structured logs and DOM snapshots.

### Core Architectural Layers

- **Core Infrastructure (`src/autonomedia/core/`)**: Houses `scheduler.py` (randomized time windows), `worker.py` (async task polling), `logger.py` (structured JSON logging via `structlog`), and `observability/monitor.py` (health metrics).
- **AI Rewriting Engine (`src/autonomedia/ai/rewriting/`)**: Stateless transformer (`RewriteProvider`) that generates platform-adapted content variants from canonical base ideas while injecting enforced whitelist contacts and links.
- **Platform Adapters (`src/autonomedia/platforms/`)**: Isolated handlers (`mastodon`, `linkedin`, `x`) wrapping Playwright browser routines or platform APIs. Each platform executes inside an isolated Chromium profile (`runtime/browser_profiles/<platform>/`).
- **Web Application (`src/autonomedia/web/`)**: FastAPI server serving domain-extracted dashboards (Command Center, Content Backlog, AI Review, Platform Health) powered by Jinja2 and HTMX.

---

## Installation

### Prerequisites

- **OS**: macOS or Linux
- **Python**: 3.12 or higher
- **Package Manager**: `uv` (required exclusively; do not use bare `pip` or `poetry`)
- **Browser**: Chromium (managed via Playwright)

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/autonomedia.git
   cd autonomedia
   ```

2. **Install dependencies using `uv`:**

   ```bash
   uv sync
   ```

3. **Install Playwright Chromium browser binaries:**

   ```bash
   uv run playwright install chromium
   ```

4. **Environment Configuration:**
   Copy the example environment file and configure your API credentials:

   ```bash
   cp .env.example .env
   ```

   Set key environment variables:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=sqlite:///./autonomedia.db  # Or postgresql+asyncpg://user:pass@localhost:5432/autonomedia
   LOG_LEVEL=INFO
   ```

5. **Initialize Database Schema:**
   ```bash
   uv run python scripts/db/migrate_db.py
   ```

---

## Usage

### 1. Launching the Web Dashboard & Command Center

Start the FastAPI application:

```bash
uv run uvicorn src.web.app:app --reload --port 8000
```

Navigate to `http://localhost:8000` in your browser to access the domain-extracted UI:

- **Command Center (`/`)**: Triage pending approvals, operational failures, and queue status.
- **Content Management (`/content-ui`)**: Create and manage canonical Idea campaigns, platforms, and schedules.
- **AI Review (`/review`)**: Inspect generated variants, compare diffs, score quality, and trigger regeneration.
- **Platform Health (`/platforms`)**: Monitor persistent browser session status and re-authentication needs.
- **Infrastructure Health (`/health`)**: System metrics, database checks, and runtime worker status.

### 2. Running Background Workers

Start the autonomous processing worker to handle background rewriting and scheduled posting:

```bash
uv run python -m autonomedia.apps.worker.main
```

### 3. Diagnostic and Platform Checks

Run system diagnostics to verify platform session health:

```bash
uv run python scripts/checks/check_platforms.py
```

Check database connection and schema integrity:

```bash
uv run python scripts/checks/check_db.py
```

---

## Design Decisions

### Local-First Autonomous Runtime

User data, credentials, and browser session cookies remain strictly local. Autonomedia does not rely on third-party SaaS publishing aggregators, preventing account bans and credential leaks while granting total execution inspectability.

### Browser-First (Playwright) over Fragile APIs

Social platform APIs are frequently paywalled, restricted, or deprecated. Autonomedia uses Playwright browser automation with persistent Chromium profiles as its primary execution layer. Automation uses accessibility-first selectors (`page.get_by_role()`, `page.get_by_label()`) rather than brittle DOM paths to remain resilient against UI redesigns.

### Async-Native Architecture

Browser automation and AI processing spend significant time waiting on I/O. Built on Python `asyncio`, the runtime handles multi-platform task queues, AI rewriting requests, and browser interactions concurrently without blocking the main event loop.

### Ephemeral Variants vs. Canonical Ideas

Canonical Ideas contain base text, reference links, and target platforms. Generated post text variants are ephemeral: created dynamically per scheduled slot, validated, posted, and discarded. This ensures infinite content freshness without database bloat.

### Whitelist Contact Truth Registry

To prevent LLM hallucination of handles, hashtags, or links, all AI rewrites pass through the Whitelist Registry (`src/autonomedia/content/mention_registry.json`). Any handle or link not present in the pre-approved whitelist is stripped or flagged prior to queueing.

### Spec-Driven Development (SDD) via AEF

As Autonomedia grew from a simple script into a multi-worker publishing pipeline, ad-hoc changes caused regressions across browser sessions and queue states. Adopting AEF/SDD enforced a 12-stage sequential engineering pipeline (Specification → Verification Protocol → Pre-Implementation TDD Evaluation → Implementation → Review → Closure), maintaining absolute system integrity.

---

## Roadmap

Autonomedia follows a phased evolution described in `docs/ROADMAP.md` and `docs/MILESTONES.md`:

### Completed Milestones

- **Milestone 0: Foundation & Core Idea Scheduling (MVP)**  
  Core `Idea` data model, custom interval scheduling engine, Gemini AI rewriting, Mastodon Playwright browser worker, and local FastAPI/HTMX dashboard.
- **Milestones 1–15 (Legacy Sequence)**  
  Browser profile isolation (M10), structured observability (M11), granular platform verification (M12/M13), randomized daily posting routines (M14), and unified multi-platform abstraction layer for Mastodon, LinkedIn, and X (M15).

### Active & Upcoming Phases

- **Milestone 1: Multi-Platform Expansion & Authentication**  
  Production OAuth 2.0 flow integration, session cookie renewal CLI, and multi-platform selection UI.
- **Milestone 2: Advanced AI & Content Control**  
  Tone style presets, automated readability scoring, and interactive Whitelist Registry editor.
- **Milestone 3: Analytics, Monitoring & Refinement**  
  Post-publish engagement ingestion (likes, reposts), token cost efficiency tracking, and self-healing session recovery.
- **Milestone 4: Extensibility & Future Growth**  
  Plugin architecture for custom AI providers, multi-tenant account isolation, agent-to-agent collaboration, and voice (TTS/STT) ingestion layers.

---

## Contributing

We welcome contributions to Autonomedia! Because the project enforces strict quality standards via AEF/SDD, please adhere to the following guidelines:

1. **Use `uv` Exclusively:**  
   Never run bare `python`, `pip`, or `pytest`. Always prefix commands with `uv run` (e.g., `uv run pytest`).

2. **Verification Before Claiming Done:**
   - Any Python file edit must be syntax-checked: `uv run python -m py_compile <file_path>`.
   - Run the test suite: `uv run pytest`.
   - Ensure imports resolve cleanly without missing package declarations in `pyproject.toml`.

3. **No Unformatted Debug Prints:**  
   Never commit `print()` or `console.log()` statements. Use the structured logger (`structlog`) imported from `autonomedia.core.logger`.

4. **Preserve Platform Isolation:**  
   Platform handlers must never share browser profiles, cookies, or DOM selectors. Maintain strict platform isolation inside `src/autonomedia/platforms/`.

5. **Spec Compliance:**  
   Specifications in `docs/` are authoritative. Code modifications must satisfy the functional requirements defined in `docs/SPEC.md` and `docs/FRAMEWORK.md`.

---

## Examples

### 1. Defining an Idea (Data Model)

```json
{
  "title": "AEF Spec-Driven Development Overview",
  "base_content": "Spec-Driven Development (SDD) replaces ad-hoc LLM coding with a deterministic 12-stage lifecycle. It ensures every requirement has explicit verification and test coverage.",
  "referral_link": "https://github.com/autonomedia/aef",
  "tags": ["SoftwareEngineering", "BuildInPublic", "AI"],
  "whitelist_contacts": ["@autonomedia_dev"],
  "style_presets": {
    "tone": "informative",
    "format": "punchy"
  },
  "platforms": ["mastodon", "linkedin", "x"],
  "frequency": "every 3 days",
  "duration_value": "1 month"
}
```

### 2. AI Rewrite Transformation (Before & After)

**Base Content:**

> "Autonomedia uses persistent browser profiles to publish scheduled content safely."

**Generated Platform Variant (Mastodon):**

> "Maintaining long-term digital presence requires persistent browser session isolation rather than brittle API tokens.
>
> Autonomedia automates scheduled publishing while keeping credentials local: https://github.com/bparlan/autonomedia
>
> Cc @bparlan
> #BuildInPublic #SoftwareEngineering"

_(Notice that `@bparlan`, the URL, and the `#hashtags` were verified against `mention_registry.json` before being marked `ready_to_post`.)_

### 3. Execution Log Output (Structured JSON)

```json
{
  "timestamp": "2026-08-24T14:32:01.402Z",
  "event": "post_published",
  "platform": "mastodon",
  "idea_id": "idea_94f82a",
  "content_id": "cnt_12a90b",
  "status": "success",
  "duration_ms": 4210,
  "screenshot_path": "storage/screenshots/mastodon_cnt_12a90b_20260824.png",
  "published_url": "https://mastodon.social/@siyah/116619458015935093"
}
```
