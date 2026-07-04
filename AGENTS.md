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

| Type                                 | Location                            |
| ------------------------------------ | ----------------------------------- |
| DB migrations / seeders / updates    | `scripts/db/`                       |
| Diagnostics / status / health checks | `scripts/checks/`                   |
| Never in project root                | utility scripts, migrations, checks |

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

## Development Protocol

### Session Hygiene

- `git status` must be clean before starting any task. Dirty tree from a
  prior session → stop, report, do not layer new edits on top.
- One task = one concern. If a task reveals a second unrelated issue
  (e.g. fixing an import breaks on a missing dependency), stop and report
  both as separate items rather than fixing the second inline.

### Verification Before Claiming Done

- Any file edit to a `.py` file: run `py_compile` on it before reporting
  success. A diff that "looks right" is not verification.
- Any import path change: `import` the actual module (not just compile)
  to catch runtime NameErrors/ModuleNotFoundErrors that compilation
  won't surface.
- Any dependency added implicitly via new code (new `import`): declare it
  in `pyproject.toml` in the same task, don't leave it to fail later.

### Rename / Move Discipline

- Any file or module rename: `grep -rn` the old path across the full
  repo before considering the task complete. Report the grep result,
  even if empty.
- Never leave two structures for the same concern (e.g. old + new
  directory both holding live code). Archive old versions explicitly
  to `_archive/`, don't delete, don't leave in place unmarked.

### Failure Reporting

- If a command fails (commit, hook, test, import), report the failure
  and stop. Do not pivot to an adjacent task and present it as if the
  original was resolved.
- If a fix cannot be fully verified (e.g. no DB access to confirm a
  migration), say so explicitly — do not present an unverified change
  as confirmed working.

### Environment

- This project uses `uv` exclusively. Never invoke bare `python`, `pip`,
  `pytest`, or `uvicorn` — always `uv run <cmd>`.
- `.python-version` is managed by `uv`; do not modify without checking
  impact on `uv sync`.

### Git Workflow

- Prefer `/commit --dry-run` to review proposed atomic splits before applying. Never invoke `/commit --push` without explicit instruction.
- Never call `git commit` directly via bash.
