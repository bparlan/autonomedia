# Milestone M5B: WebPanel

## Goal
Establish a browser-first administration dashboard to observe, manage, and verify content lifecycle (Idea -> Approved -> Posted). This dashboard provides the observability required to safely introduce the AI Rewrite Layer in M6.

## Architecture
- **Framework**: FastAPI (Async)
- **UI/Interactivity**: HTMX (Server-side rendering, minimal JS)
- **Integration**: Direct connection to `src/database/client.py`

## Features
- [ ] Content List View (Data Grid)
- [ ] CRUD Operations (Add, Edit, Delete)
- [ ] Status Toggling (Idea / Approved / Posted)
- [ ] Search/Filter by Status
- [ ] Preview Modal (Skeleton)

## Success Criteria
- [ ] Panel is accessible in the browser.
- [ ] Changes in Panel are immediately reflected in PostgreSQL.
- [ ] No complex JS dependencies (strictly HTMX).
- [ ] Operational logs verify accessibility of the panel.
