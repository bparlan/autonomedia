# UI Template & Route Inventory

This document maps all web templates found in the repository to their classification (End-User vs. Admin/Internal) and their associated API route and handler.

## Template Classification

| Template File | Classification | Primary Use-Case | Served By Route | Handler Function |
|--------------|---------------|-----------------|-----------------|------------------|
| `web/templates/dashboard.html` | End-User | Primary Idea operations view (Idea Backlog, Status, Execution Logs) | `GET /dashboard` | `src.autonomedia.web.router:get_dashboard_page` |
| `web/templates/health_dashboard.html` | End-User | Real-time system health and task queue monitoring | `GET /health` | `src.autonomedia.web.api.health:get_health_status` |
| `web/templates/index.html` | End-User | Application entry point / Landing page | `GET /` | `src.autonomedia.web.main:root` |
| `web/templates/platforms.html` | End-User | Session health, OAuth/auth management for Mastodon & other platforms | `GET /platforms` | `src.autonomedia.web.router:get_platforms_page` |
| `web/templates/registry.html` | End-User | Whitelist contact & mention registry editor (`mention_registry.json`) | `GET /registry` | `src.autonomedia.web.router:get_registry_page` |
| `web/templates/review.html` | End-User | AI Review screen (Diffing, scoring, and regenerating platform rewrites) | `GET /review` | `src.autonomedia.web.router:get_review_page` |
| `web/templates/content.html` | End-User | Detailed content & Idea management table | `GET /content-ui` | `src.autonomedia.web.api.content:get_all_content` |
| `web/templates/rewrites.html` | End-User | Overview of AI rewrites per Idea | `GET /rewrites` | `src.autonomedia.web.router:get_rewrites_page` |
| `web/templates/health.html` | Admin/Internal | Fallback static health monitoring page | `GET /health-static` | Static file fallback |
| `web/templates/base.html` | Internal | Base Jinja2 layout template with common header/navigation | N/A (Included by others) | N/A |
| `web/templates/partials/content_row.html` | End-User | HTMX partial for rendering an individual Content/Idea row | `GET /partials/content-row/{id}` | `src.autonomedia.web.api.content:get_content_row_partial` |
| `web/templates/partials/content_status.html` | End-User | HTMX partial for updating Idea posting status badge | `GET /partials/content-status/{id}` | `src.autonomedia.web.api.content:get_content_status_partial` |
| `web/templates/partials/row.html` | End-User | HTMX partial for generic table rows | `GET /partials/row/{id}` | Generic partial handler |
| `web/templates/partials/content_edit_form.html` | End-User | HTMX partial form for creating/editing an Idea | `GET /partials/content-edit-form/{id}` | `src.autonomedia.web.api.content:get_content_edit_form` |
| `web/templates/partials/edit_form.html` | End-User | HTMX partial form for inline editing | `GET /partials/edit-form/{id}` | Generic edit form handler |
| `web/templates/partials/review_form.html` | End-User | HTMX partial form for submitting AI review feedback | `POST /partials/review-form/{id}` | `src.autonomedia.web.api.content:submit_review_form` |

## Summary Findings

1. **End-User Pages:** `dashboard.html`, `health_dashboard.html`, `index.html`, `platforms.html`, `registry.html`, `review.html`, `content.html`, `rewrites.html`, and all partials in `web/templates/partials/`.
2. **Admin/Internal Pages:** `health.html` (static fallback), `base.html` (layout wrapper).
3. **Primary Gap:** The HTML templates currently reside under `web/templates/` (root-level) rather than being served directly by FastAPI routes in `src/autonomedia/web/main.py`. These routes need to be formally wired with Jinja2Templates to make the application fully functional.
