# Interaction Matrix – Core ↔ Platform Adapters ↔ DB ↔ Observability

| Component | Sub‑modules | Primary Responsibilities | Key Interfaces / Calls |
|-----------|------------|---------------------------|------------------------|
| **Core Services** | `core/posting_routine.py`, `core/scheduler.py`, `core/poller.py`, `core/worker.py` | Orchestrates Idea lifecycle: scheduling, AI rewrite request, dispatch to platform adapters, persisting results. | Calls `ai/rewrite/*` for text generation, invokes `platform/*/task_handler.py` for posting, writes to DB via SQLAlchemy models (`Content`, `Like`, etc.), emits metrics to `observability/monitor.py`. |
| **Platform Adapters** | `platforms/mastodon/task_handler.py`, `platforms/linkedin/task_handler.py`, `platforms/bluesky/task_handler.py` (future) | Translate canonical content into platform‑specific API calls (or browser automation via Playwright). Handles auth/session via isolated Chromium profiles. | Receives normalized payload from Core, returns status (`success`/`error`), logs to `observability/monitor.py`. |
| **Database (SQLite)** | `database/client.py`, ORM models in `web/models.py` | Stores canonical Ideas, posting logs, AI rewrite history, whitelist registry (`mention_registry.json`). | Core reads/writes `Content` rows, Platform adapters may log posting metadata, Observability reads health‑check tables. |
| **Observability** | `observability/monitor.py`, `web/templates/health.html` | Provides health metrics (DB connection, runtime, test suite, source integrity) and runtime statistics (queue depth, error rates). | Exposed via `/api/health` endpoint, polled by dashboard UI; Core updates counters via `monitor.log_event()`. |

**Notes**
- All cross‑component calls are performed via Python function calls (no network RPC) because the system runs as a single process with async workers.
- Platform adapters use Playwright sessions stored under `runtime/browser_profiles/` which are isolated per platform.
- The whitelist JSON lives at `src/autonomedia/content/mention_registry.json` and is loaded by the `entity_normalizer` during ingestion.
