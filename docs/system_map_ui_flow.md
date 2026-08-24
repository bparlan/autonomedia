# Content Creator Journey – Idea Management

## Overview
The **Content Creator** (primary user persona) interacts with Autonomedia through a small set of UI pages that support the full lifecycle of an **Idea** – from initial definition to automated, recurring posting.

## Journey Steps
1. **Landing / Dashboard** (`/` – `index.html` placeholder)
   - Shows a high‑level summary of active Ideas, next scheduled posting, and health status.
   - Quick‑access buttons: *Create New Idea*, *View All Ideas*, *Analytics*.

2. **Create Idea Form** (`/idea/new` – could be rendered by `dashboard.html` or a modal)
   - **Fields** (as defined in the Idea data model):
     - *Title* – short human readable name.
     - *Base Text* – the canonical content.
     - *Referral Link* – optional URL to share.
     - *Tags / Hashtags* – free‑form list.
     - *Whitelist* – multi‑select of pre‑approved contacts/handles (pulled from `mention_registry.json`).
     - *Platforms* – checkboxes for supported platforms (Mastodon MVP).
     - *Duration* – relative selector (e.g. “1 month”, “2 weeks”). Internally stored as start‑date + auto‑computed end‑date.
     - *Frequency* – custom interval input (e.g. “every 3 days”).
     - *AI Rewrite Style* – dropdown (Formal, Casual, Marketing) plus optional tone presets.
   - **Actions**: *Save* (creates DB row, schedules first posting) or *Cancel*.

3. **Idea Backlog / Management Page** (`/ideas` – `content.html` placeholder)
   - Tabular view of all Ideas with columns:
     - Title, Platforms, Status (Active / Completed), Next Post, Frequency, Remaining Posts.
   - Row actions: *Edit*, *Delete*, *Pause/Resume*, *View History*.
   - Inline edit support via HTMX partials (`partials/content_edit_form.html`).

4. **Edit Idea** (`/ideas/{id}/edit`)
   - Re‑uses the Create form populated with current values.
   - Allows adjusting schedule, platforms, whitelist, or AI style.
   - Saving updates the DB record and re‑calculates the posting schedule.

5. **AI Review Screen** (`/review` – `review.html` placeholder)
   - After each generated rewrite, the creator can view a diff, accept or request regeneration.
   - Provides a *Score* (e.g., token usage, readability) and a *Regenerate* button.

6. **Posting Execution** (background, not UI) – triggered by the **Scheduling Engine**.
   - Posts are created, AI‑rewritten, sent to the platform adapter, and status persisted.
   - UI receives updates via periodic polling or WebSocket (future enhancement).

7. **Analytics Dashboard** (`/analytics` – `rewrites.html` placeholder)
   - Shows per‑Idea posting count, engagement metrics (likes, replies), and AI rewrite success rates.
   - Exportable CSV / JSON for downstream analysis.

## Interaction Highlights
- **Whitelist Integration**: The *Mention Registry* JSON is loaded client‑side for selection and validated server‑side before posting.
- **Platform‑Specific Rendering**: The rewrite engine receives the *platform* identifier to apply length limits and syntax (e.g., Mastodon 500‑char limit).
- **Feedback Loop**: The *AI Review* step can flag low‑quality rewrites, feeding back into a *retry‑counter* that limits regeneration attempts.

## Future Enhancements
- Real‑time status updates via Server‑Sent Events.
- Drag‑and‑drop reordering of Ideas to prioritize posting.
- Multi‑platform simultaneous posting with per‑platform enable toggles.

*This journey map is intentionally high‑level; implementation details (routing, template names) will be refined during the next development sprint.*
