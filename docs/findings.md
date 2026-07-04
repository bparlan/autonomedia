# Architecture Findings - M14S1 Review

## Resolved Issues

### Issue: Unvalidated Timing Window Logic
**Pattern:** The implementation includes logic for 8-hour window between posts (lines 200-214 in `posting_routine.py`), but no test case validates this behavior. The logic `if (now - last_posted) >= timedelta(hours=SECOND_POST_MIN_HOURS)` is untested, creating risk of incorrect scheduling behavior in production.

**Resolution:** ✅ FIXED - Added `test_second_execution_within_8_hours_no_additional` and `test_execution_after_8_hours_second_item_allowed` tests that insert controlled `post_history` timestamps.

### Issue: Defined-But-Unused Function Pattern
**Pattern:** `_apply_randomized_delay()` is defined (line 45) but never invoked in `posting_routine()`. This creates a false sense of completeness - the function exists, tests mock it, but the actual business requirement (randomized delays) is unmet.

**Resolution:** ✅ FIXED - Added `await _apply_randomized_delay()` call in `posting_routine()` before processing items (lines 213-215).

### Issue: Spec Coverage Gap in Test Suite
**Pattern:** Verification document specifies TC3, TC9, TC10 but test suite only has TC1, TC2, TC4, TC5, TC6, TC7, TC8, TC11. This creates incomplete test coverage for specified behaviors.

**Resolution:** ✅ FIXED - Added TC3, TC9, TC10 tests to `tests/test_m14_routine.py`.

## Outstanding Issues

### Issue: Legacy Code Path Conflict Risk
**Pattern:** `PostingWorker` in `posting_executor.py` exists alongside `posting_routine()`. Both can query `ready_to_post` without coordination. The M14S1 spec states the old worker "posts content regardless of platform verification state."

**Recommendation:** Either deprecate `PostingWorker` or add a compatibility layer that prevents simultaneous execution.

This remains as a potential operational hazard if both workers are active.