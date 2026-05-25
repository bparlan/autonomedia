# AUTONOMEDIA — PLAYBOOK.md

# DEVELOPMENT RULES

1. Build smallest working version first.
2. Prefer inspectability over cleverness.
3. Avoid abstraction until repeated pain appears.
4. Keep AI layer thin and strictly moderated.
5. Preserve platform isolation.
6. Always capture failures (Screenshots, Logs).
7. Prefer boring reliability.

---

# UX/UI RULES

1. **Extract Domains:** Do not cram all operations into a monolithic table or an infinite scrolling screen.
2. **Command Center is an Inbox:** The root view should only contain items that require human operator action (approvals, failed jobs, quick triage).
3. **One-Click Resolutions:** Design flows so that fixing a failure or approving a post takes exactly one click from the operational view.
4. **AI is a Workflow:** Do not treat AI review as a single HTML box. It requires diffs, traces, and platform-specific checks. Build it as a first-class subsystem.

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
