# Autonomedia Dashboard Test Scenarios

This document outlines 10 critical user flows for the Autonomedia Assembly Dashboard, ensuring full coverage of CRUD operations, protection layers, and UI integrity.

---

## Standard Scenarios

## Scenario 01: Create New Content Entry
**Goal:** Verify successful addition of content.
**Verification:**
- **UI:** Row appears without duplication.
- **Data:** `SELECT * FROM content WHERE id='...'` confirms record exists.

## Scenario 02: Toggle Content Status
**Goal:** Verify status toggle (idea <-> approved).
**Verification:**
- **UI:** Row background updates to green on "approved".
- **Data:** `SELECT status FROM content WHERE id='...'` matches UI state.

## Scenario 03: Edit and Save Content
**Goal:** Verify inline editing works for unapproved content.
**Verification:**
- **UI:** Edit form spans 4 columns, saves without duplication.
- **Data:** Updated fields persist in DB.

## Scenario 04: Delete Content Entry
**Goal:** Verify removal of unwanted content.
**Verification:**
- **UI:** Row disappears immediately.
- **Data:** `SELECT count(*) ...` returns 0 for that ID.

## Scenario 05: Cancel Edit Flow
**Goal:** Verify edit mode cancellation.
**Verification:**
- **UI:** Row reverts to original content, no edit persisted.
- **Data:** No DB update performed.

---

## Complex Scenarios

## Scenario 06: Approval Lock Enforcement
**Goal:** Verify that "approved" content cannot be edited or deleted.
1. **Action:** Toggle a row to "Approved".
2. **Action:** Observe row background color change.
3. **Verification:**
- **UI:** "Edit" (✎) and "Delete" (🗑) buttons disappear, replaced by "LOCKED".
- **Data:** Attempting to manually `DELETE` or `UPDATE` this ID via backend should be blocked by business logic (or UI prevents access).

## Scenario 07: Data Integrity on Partial Edit
**Goal:** Ensure fields not included in the edit form are not corrupted (nullified).
1. **Action:** Edit a content row.
2. **Action:** Change Topic, submit.
3. **Verification:**
- **Data:** Query DB to ensure `source_idea`, `link_url`, `hashtags`, and `mentions` remain unchanged.

## Scenario 08: Empty Field Handling
**Goal:** Verify behavior when submitting edits with empty fields (if allowed).
1. **Action:** Edit a content row.
2. **Action:** Clear all input fields.
3. **Verification:**
- **UI:** Form validation (HTML5 `required` attribute) prevents empty submission.
- **Data:** No partial/empty data is written to the DB.

## Scenario 09: Rapid State Change (Toggle Stress Test)
**Goal:** Verify UI responsiveness and state consistency under rapid toggling.
1. **Action:** Quickly click the status checkbox 3 times in succession.
2. **Verification:**
- **UI:** Checkbox ends in the correct state matching the database.
- **Data:** Final DB status matches the UI state.

## Scenario 10: Hashtag/Mention Complexity
**Goal:** Ensure special characters or complex inputs handle parsing.
1. **Action:** Add content with complex hashtags (e.g., `#web3-dev, #AI-Research`) and mentions.
2. **Verification:**
- **UI:** Tags/Mentions render correctly as individual badges.
- **Data:** JSONB structure in DB stores them as clean arrays.
