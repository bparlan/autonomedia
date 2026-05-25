# Grill: Dashboard Architecture
- **Intent:** Scale the Autonomedia UI from a Phase 1 "Monolith Surface" to a Phase 3 "Domain Extraction" to support an autonomous media operations system.
- **Constraints:** Avoid framework soup (no React/Vue). Emphasize "fewer clicks to resolve work" over "fewer pages".
- **Key Decisions:** 
  - Adopt a multi-page Information Architecture with a unified navigation shell.
  - Command Center becomes an operational overview/triage inbox, NOT a management screen.
  - Extract AI Review, Content, Platforms, and Analytics into first-class subsystems.
- **Assumptions:** AI Review requires complex workflows (diffs, regens, traces) that cannot fit in a table cell. Analytics is a feedback engine, not vanity charts.
- **Open Questions:** What is the exact sequence of Milestones to execute this extraction?
- **Out of Scope:** Infinite scrolling, mega-dashboards, heavy modal workflows.
