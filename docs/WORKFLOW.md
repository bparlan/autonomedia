# Autonomedia Operational Workflow

## Daily Workflow (The Engine Layer)
1. **Start**: `pi-sync --session`. Review the `task_plan.md` preview Pi generates. 
   *   *HITL Confirmation*: Explicitly tell Pi, "Confirmed, let's start M[X]."
2. **Execute**: Work on tasks. Log progress in `progress.md`. 
3. **Discover**: If you hit a technical hurdle, log the solution in `findings.md` immediately (The "2-Action Rule").
4. **End**: Summarize the day's `progress.md` into `task_plan.md` status. 
   *   *HITL Confirmation*: Pi asks, "Shall I save session state?" You confirm.

## Weekly Workflow (The Consistency Layer)
1. **Audit**: `pi-sync --audit`. 
2. **Review**: Look at `CHANGELOG.md`. Ensure it reflects the *milestone-level* progress, not just daily commits.
3. **Prune**: Run a manual check on `/docs/milestones/` to ensure no "stale" specs exist for tasks you've already completed.

## New Milestone Methodology
1. **Define**: Create `docs/milestones/M{X}-NAME.md`. Copy the template from existing milestones.
2. **Map**: Update `ROADMAP.md` with the new Milestone row.
3. **Initialize**: Run `task_plan.md` and append the new Milestone sections (with empty `[ ]` tasks).
4. **Approve**: Pi presents the new plan. 
   *   *HITL Confirmation*: You verify the milestone scope *before* a single line of code is written.
