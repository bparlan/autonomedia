# AUTONOMEDIA — PLAYBOOK.md

# DEVELOPMENT RULES

1. Build smallest working version first.
2. Prefer inspectability over cleverness.
3. Avoid abstraction until repeated pain appears.
4. Keep AI layer thin.
5. Preserve platform isolation.
6. Always capture failures.
7. Prefer boring reliability.

---

# FIRST IMPLEMENTATION TARGET

DO NOT start with:
- LinkedIn
- X
- Facebook

Start with:
1. Mastodon
2. Bluesky

Reason:
- easier automation surfaces
- faster iteration
- lower anti-bot hostility

---

# COMMON FAILURE MODES

## Fragile Selectors

Fix:
- accessibility selectors
- semantic targeting
- avoid CSS chains

---

## Session Corruption

Fix:
- isolated profiles
- backup profiles
- avoid shared state

---

## AI Overreach

Fix:
- deterministic orchestration
- AI only for transformations

---

## Logging Blindness

Fix:
- structured logs
- screenshots
- verification steps

---

# IMPORTANT ARCHITECTURAL WARNING

Do not accidentally build:
- Hootsuite clone
- LangChain maze
- autonomous swarm system
- recursive self-improving agent

Build:
- operationally reliable publishing infrastructure.
