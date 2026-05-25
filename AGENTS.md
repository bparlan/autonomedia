# AUTONOMEDIA — AGENTS.md
> Extends default AGENTS.md. Safety protocols and tool rules are inherited.

## SYSTEM IDENTITY
Local-first autonomous publishing runtime.
Deterministic. Inspectable. Modular. Browser-first. Async-native.

## PRIMARY GOALS
1. Reliable autonomous posting
2. Human-like browser automation
3. Minimal operational overhead
4. Durable architecture
5. Structured observability
6. AI augmentation without AI dependency
7. Long-term extensibility

## ENGINEERING PRINCIPLES
- **Reliability > Intelligence**: System must function without OpenRouter, Ollama, or AI rewrites.
- **Deterministic Execution**: Every task produces logs, screenshots, post verification, structured result. No silent failures.
- **Browser-First**: Playwright is primary. No API-first assumptions, no provider lock-in.
- **Modularity**: Rewrite provider, scheduler, analytics, browser backend, queue — each independently replaceable.

## AI USAGE POLICY
Permitted: rewrite generation, shortening, tone adaptation, CTA optimization, analytics summarization.
Prohibited: runtime orchestration, queue management, browser state control, recursive planning.

## NAVIGATION
- Begin every session: `read /INDEX.md`.
- Tri-Tier Sync: use `pi-sync` skill + `/journal.md` template.
- Never make state-changing updates (Roadmap/Milestone) without explicit user approval.
