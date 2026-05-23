# Milestone M5C: WebPanel Issues & Tasklist

## Current Status (M5B Evaluation)
The M5B WebPanel foundation is built, but functionality is inconsistent. The dashboard is not yet fully reliable for 40+ content items due to routing and UX bugs in the interaction layer.

## Tasklist
- [ ] **Critical Fix: Routing (404s):** Stabilize `add` and `delete` endpoints.
- [ ] **Critical Fix: Toggle Status:** Ensure checkbox state is purely boolean (ticked/empty) and updates database reliably without UI artifacts.
- [ ] **UX Fix: Layout:** Move "Add Content" form below the page title.
- [ ] **UX Fix: Category Manager:** Integrate category selection ("RefLink", "SelfPromotion", "Social") in the "Add" form.
- [ ] **UX Fix: Variable Input:** Add a simple text-based interface for comma-separated hashtags and mentions in the Add/Edit form.
- [ ] **Functionality: Edit Flow:** Implement a functional edit mechanism (replacing the "will be implemented" alert).
- [ ] **Stability: Validation:** Ensure database schema integrity remains across all CRUD operations.

## Architecture Guidelines
- All interactive actions must use HTMX (no page reloads).
- UI must remain compact (full-width usage).
- Data must be isolated (Idea, Link, Tags, Mentions).
