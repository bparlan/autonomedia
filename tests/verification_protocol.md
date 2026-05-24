# Autonomedia Dashboard Verification Protocol

This protocol defines how to verify the successful execution of each workflow in `tests/scenario01.md`.

| Scenario | Action | Verification Method |
| :--- | :--- | :--- |
| **01 (Add)** | Click "Add Content" | 1. Query DB: `SELECT * FROM content WHERE topic='AI Reliability'` returns 1 row.<br>2. UI: New row appears in DOM. |
| **02 (Toggle)** | Click Checkbox | 1. Query DB: Status column toggles between 'idea' and 'approved'.<br>2. UI: Checkbox state matches DB status. |
| **03 (Edit)** | Click "Save" | 1. Query DB: `topic` field matches input.<br>2. UI: Table row displays new text. |
| **04 (Delete)** | Click "Delete" | 1. Query DB: `SELECT count(*) FROM content WHERE id='...'` returns 0.<br>2. UI: Table row removed from DOM. |
| **05 (Cancel)** | Click "Cancel" | 1. Query DB: No changes persisted.<br>2. UI: Row reverts to original state. |

---

## Execution: Scenario 01 (Add Content)

I will execute the first scenario now by manually adding a record through the backend logic to verify the infrastructure, then verify via the DB.

*Note: Since I cannot click a browser UI, I will execute the Python code equivalent to the "Add" button action.*

### 1. Pre-Execution Check
- Verify current count of content items.
