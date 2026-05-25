# pi-sync Journaling System

## Tiers Overview
1. **Session Tier** (User Execution)
- Human‑in‑the‑loop confirmations
- Progress tracking in `progress.md`
- Milestone status updates

2. **Milestone Tier** (HITL/Formal Tracking)
- Milestone‑specific docs: `CHANGELOG.md`, `docs/milestones/M12.md`
- Audit artifacts: `M12_FINDINGS_ARCHIVE.md`

3. **Audit Tier** (Automated Compliance)
- Runtime/safety checks: `git diff --name-only | grep -E "runtime|cache|profile|session|artifact|token|secret"`
- Version tracking: `git log --oneline --decorate`

## Staging & Pushing Workflow
### Phase 1: Staging
- **Command**: `git add [files]`
- **Example**:
  ```bash
  git add src/ scripts/ README.md CHANGELOG.md progress.md .gitignore justfile
  ```
- *Requirements*: All modified files must be added
- *pi‑sync Sync*: `pi-sync --session` updates session state

### Phase 2: Verification
- **Command**: `git diff --cached --stat`
- **pi‑sync Interaction**:
  ```
  pi-sync --audit --alert-on-changes
  ```
- *Purpose*: Confirm staged changes match expectations

### Phase 3: Commit
- **Command**: `git commit -m "[scope]: concise summary"`
- **Example**:
  ```bash
  git commit -m "docs(changelog): add M12 AI rewrite pipeline, resilience, platform verification"
  ```
- *pi‑sync Sync*: `pi-sync --milestone` updates milestone metadata

### Phase 4: Push
- **Command**: `git push origin main`
- **pi‑sync Sync**: `pi-sync --commit` records the push
- *Requirements*: Remote must be synchronized

### Phase 5: PR Creation (Optional)
- **Command**:
  ```bash
  git push --set-upstream origin main
  # On GitHub: Create PR from main
  ```
- *pi‑sync Interaction*: `pi-sync --pr` confirms PR state

## Critical Notes
- All commands must be executed in **/Users/bparlan/devcode/autonomedia**
- Never bypass `pi-sync` commands without HITL confirmation
- Journal updates must be written after each phase attempt