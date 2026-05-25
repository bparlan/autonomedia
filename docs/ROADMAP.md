# AUTONOMEDIA — ROADMAP.md

# COMPLETED MILESTONES

## Foundation & Browser Setup (M1-M4)
- Postgres connection pool established.
- Playwright Chromium profiles persisted.
- Basic routing and FastAPI setup.
- Basic Mastodon task handler.

## AI & The Assembly Line (M5-M6)
- Replaced direct scripts with an async Assembly Line (`idea -> approved -> prepared -> published`).
- Integrated `google-genai` with model fallback chains.
- Split operations into independent `PostingSecretary` (AI) and `PostingExecutor` (Browser).

## Moderation & Guardrails (M7)
- Implemented `ModerationAdapter` to block content that violates platform limits.
- Added Browser Profiling (randomized viewports, human delays) to prevent bot detection.
- Prevented duplicate posts with a relational `post_history` check.
- Enforced a human-in-the-loop review step for all AI generations.

---

# CURRENT & UPCOMING MILESTONES

See full specifications in `docs/milestones/`.

## PHASE 3: Domain Extraction & UX (M8)
- **Status**: COMPLETE
- **Specs**: [M8 UX Architecture](docs/milestones/M8-UX-ARCHITECTURE.md)

## PHASE 4: Platform Health & Feedback (M9)
- **Status**: IN_PROGRESS
- **Specs**: [M9 Platform & Analytics](docs/milestones/M9-PLATFORMS-AND-ANALYTICS.md)

## PHASE 5: Autonomous Runtime (M10)
- **Status**: PENDING
- **Specs**: [M10 Autonomous Runtime](docs/milestones/M10-AUTONOMOUS-RUNTIME.md)

## PHASE 6: Observability & Self-Healing (M11)
- **Status**: PENDING
- **Specs**: [M11 Observability](docs/milestones/M11-OBSERVABILITY-AND-SELF-HEALING.md)


---

# FUTURE PHASES (M10+)

## Cross-Platform Expansion
- Deploy LinkedIn task handler.
- Deploy X (Twitter) task handler.
- Standardize multi-platform parallel publishing.

## Advanced Analytics & Memory
- Ingest engagement data (likes, reshares).
- Build semantic memory context for the AI to "remember" past successful tones.
- Implement cost/performance ratio tracking.