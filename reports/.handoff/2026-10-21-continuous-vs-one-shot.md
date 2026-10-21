# theteam — Identify major functions in the autonomedia codebase that are candidates for continuous/long-running usage vs one-shot entrypoints

- **Project:** autonomedia
- **Generated:** 2026-10-21 06:59 UTC
- **Members reporting:** architect, data, devops, funding_strategist, pragmatist, skeptic

## Individual notes

Each member's note below was written independently, before the synthesis pass — no member has seen another's note.

### (see completion) (`architect`)

**Verdict:** {
  "completion": "Completed classification and coupling assessment of key components in autonomedia.",
  "confidence": 

{
  "completion": "Completed classification and coupling assessment of key components in autonomedia.",
  "confidence": 0.95,
  "actions_taken": [
    {
      "tool": "glob",
      "result": "Surveyed

### (see completion) (`data`)

**Verdict:** {
  "completion": "{\"id\":\"data\",\"role\":\"Data & Analytics Lead\",\"verdict\":\"Most autonomedia functions are CONT

{
  "completion": "{\"id\":\"data\",\"role\":\"Data & Analytics Lead\",\"verdict\":\"Most autonomedia functions are CONTINUOUS (scheduler/poller/worker/monitor/platform handlers/AI pipeline/web routes

### (see completion) (`devops`)

**Verdict:** {
  "completion": "Classified autonomedia major functions as CONTINUOUS or ONE-SHOT with DevOps observations.",
  "confi

{
  "completion": "Classified autonomedia major functions as CONTINUOUS or ONE-SHOT with DevOps observations.",
  "confidence": 1,
  "actions_taken": [
    {
      "tool": "glob",
      "result": "Sur

### (see completion) (`funding_strategist`)

**Verdict:** {
  "completion": "Identified continuous (product-facing) vs one-shot (support) functions. The core continuous functions

{
  "completion": "Identified continuous (product-facing) vs one-shot (support) functions. The core continuous functions are scheduler loop (scheduler:process_ready_ideas), posting routine with random

### (see completion) (`pragmatist`)

**Verdict:** {
  "completion": "Analyzed autonomedia codebase for continuous vs one-shot functions, identified over-engineering, and 

{
  "completion": "Analyzed autonomedia codebase for continuous vs one-shot functions, identified over-engineering, and mapped core posting loop.",
  "confidence": 0.95,
  "actions_taken": [
    {

### (see completion) (`skeptic`)

**Verdict:** {
  "completion": "Adversarial review complete. Identified 14 major functions across the autonomedia codebase, classifie

{
  "completion": "Adversarial review complete. Identified 14 major functions across the autonomedia codebase, classified as CONTINUOUS (long-running) vs ONE-SHOT entrypoints, with detailed evidence o

## Consolidated report

All six members agree that autonomedia's core is a set of continuous long-running loops (scheduler, worker/poller, posting routine, posting secretary, posting executor, health monitor, Telegram bot, web routes) plus a handful of one-shot entrypoints (CSV ingest, healthcheck, manual run_one_shot, per-idea AI analysis). Disagreement is limited to emphasis: the Data member flags in-memory state (DatabaseClient._pool, asyncio.Queue, handler instances) as the single point of failure for data continuity, while the others treat it as an operational detail.

**Where the team agreed:**

- scheduler_loop (scheduler.py) is CONTINUOUS — 60s polling loop over the content table.
- worker + poller pair (core/worker.py) is CONTINUOUS — queue-based consumer with 10s poll interval.
- posting_routine (core/posting_routine.py) is CONTINUOUS — daily randomized-interval posting loop.
- PostingSecretary (agents/posting_secretary/worker.py) is CONTINUOUS — 30s agent loop.
- PostingWorker (apps/worker/posting_executor.py) is CONTINUOUS — 30s polling loop.
- PassiveHealthMonitor (core/observability/monitor.py) is CONTINUOUS — periodic platform health poller.
- TelegramNotifier (core/observability/telegram.py) is CONTINUOUS — long-lived bot with start_polling.
- Platform task_handlers (mastodon/x/linkedin) are CONTINUOUS — persistent browser sessions via BrowserProvider.
- FastAPI app (web/app.py) and API router are CONTINUOUS — long-lived HTTP routes.
- BrowserProvider is context-managed per-call, not a persistent process.
- scripts/ingest_content.py (ingest_csv) is ONE-SHOT.
- src/autonomedia/ai/analysis.py (perform_ai_analysis) is ONE-SHOT — invoked per idea.
- src/autonomedia/ingestion/content_ingestor.py (capture_content_idea) is ONE-SHOT — pure function.
- run_manual.py (run_one_shot) is ONE-SHOT — boot-and-post CLI entrypoint.
- checks/healthcheck.py is ONE-SHOT — snapshot check.

**Where the team disagreed:**

- {'topic': 'Severity of in-memory state loss on restart', 'positions': ['Data member: DatabaseClient._pool, asyncio.Queue, and handler instances are all lost on restart; this is the SPOF for data continuity. No Redis/queue persistence exists — in-flight tasks vanish on crash.', 'Other members: treat the DB as the source of truth and the in-memory structures as transient caches; they flag the coupling but do not rank it as the top risk.'], 'resolution': "The Data member's observation is technically correct and better evidenced (they read database/client.py and schema.py directly). The disagreement is one of emphasis, not fact."}

**Open questions for you:**

- Is there a deployment model where more than one continuous loop runs in the same process? If so, their asyncio.Queues and handler instances share memory and a single crash takes all of them down.
- What is the recovery contract when PostgreSQL is down at boot? Every continuous loop fails until it recovers — is that acceptable, or does the scheduler need a startup delay/retry?
- Verification status (verified/verified_at/expires_at per platform, JSONB in the content table) is the only cross-restart record of human approval. Is the expiry logic actually enforced anywhere, or can verified ideas sit in the queue indefinitely?

**Recommendation:**

No consensus-breaking dispute — the classification is stable across all six members. Treat the continuous loops as the product surface and the one-shots as operational tooling. The one actionable item the team converges on: the in-memory state (DatabaseClient._pool class cache, asyncio.Queue, per-handler browser instances) is lost on any restart, and there is no queue persistence. If autonomedia is expected to survive process crashes without losing in-flight posts, that state needs to be either durably queued or reconstructed from PostgreSQL on startup. For now, the honest recommendation is to document the restart contract explicitly rather than to refactor — the current design is coherent, just undocumented.
