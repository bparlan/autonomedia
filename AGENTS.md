# AUTONOMEDIA — AGENTS.md
> Extends default AGENTS.md. Safety protocols and tool rules inherited.

## IDENTITY
Local-first autonomous publishing runtime. Deterministic. Modular. Browser-first. Async-native.

## NAVIGATION
- You already possess the complete directory structure in your system instructions.
- NEVER run `ls -R`, `find .`, or any unbounded directory listing commands.
- Use `search_code(query)` for file lookup.
- Prefer `skeletons → full file`. Always read `./docs/skeletons/` first.
- Call `read` or `bash` before any `write` or `edit`.
- NEVER use `write` on existing files. Use `edit` instead.
- Run `generate_skeletons()` after major changes.
- Load full file only when skeleton is insufficient.

## FILE PLACEMENT
| Type | Location |
|---|---|
| DB migrations / seeders / updates | `scripts/db/` |
| Diagnostics / status / health checks | `scripts/checks/` |
| Never in project root | utility scripts, migrations, checks |

## DOMAIN CONSTRAINTS
- Package manager: `uv` only. No `pip`, no `poetry`.
- Browser: Playwright only. Accessibility-first selectors (`get_by_role` preferred).
- Every task must produce: logs, screenshot, post verification, structured result. No silent failures.
- Modules (provider, scheduler, analytics, browser backend, queue) are independently replaceable.
- System must be operable without AI rewrites.

## AI POLICY
**Permitted:** rewrite generation, shortening, tone adaptation, CTA optimization, analytics summarization.
**Prohibited:** runtime orchestration, queue management, browser state control, recursive planning.

## ARCHITECTURE MAP
```
~/devcode/autonomedia/
├── docs/
│   ├── ROADMAP.md       # Vision
│   ├── SPEC.md          # Functional requirements
│   ├── FRAMEWORK.md     # Design principles & stack rules
│   ├── DATA.md          # DB schema & storage
│   ├── PLAYBOOK.md      # Operator guide & failure modes
│   ├── CHANGELOG.md     # Version history
│   ├── WORKFLOW.md      # Operational cadence
│   ├── state.json       # Active lifecycle state
│   ├── milestones/      # Milestone objectives
│   ├── specs/           # Active technical specs
│   ├── verifications/   # Quality gates & test plans
│   ├── reviews/         # Reality vs. plan audits
│   └── archive/         # Completed milestone learnings
├── runtime/       # Async/queue flow
│   ├── browser_profiles
│   ├── sessions
│   └── tmp
├── scripts/
│   ├── checks/          # Diagnostics & platform verifications
│   └── db/              # Migrations & schema updates
├── src/                 # Application code
├── tests/               # Unit, integration, e2e
├── runtime/             # Ephemeral state (browser profiles, sessions)
└── storage/             # Persistent outputs (logs, screenshots, exports)
```
