# Autonomedia Revision Rules

If the review fails, the agent must abide by these rules when applying fixes:

1. **The Spec is Law:** You cannot change the `docs/specs/` or `docs/verifications/` files to make the tests pass. If the code cannot meet the spec, the code is wrong. 
2. **Surgical Edits Only:** Do not rewrite entire files to fix a minor issue. Use the `edit` tool to specifically target the broken lines.
3. **Iron Law of Debugging:** If tests are failing, diagnose the root cause *before* changing code. Form a hypothesis, and test one hypothesis at a time.
4. **Run Tests After Every Fix:** You must run `just test` and verify the `exitCode` before deciding a revision is complete.
