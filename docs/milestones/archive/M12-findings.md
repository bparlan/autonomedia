# Findings Archive - M13 AI Rewrite

## Current Architecture Status
- **Batching**: Implemented `/batch-generate` via `asyncio.create_task` in `src/web/app.py`.
- **AI Provider**: `GeminiProvider` is integrated. Fixed `NameError` by adding `RewriteContext` import.
- **Data Model**: `content` table `status` column drives the UI split between `/content` (idea) and `/rewrites` (approved/prepared).
- **Templates**: `content_row.html` is used by both views, but logic inside might need tightening (buttons show based on status).

## Constraints / Blind Spots
- **Resumeability**: The current implementation of `process_rewrites` selects *all* `rewriting` items. If a process dies, it will pick them up again on restart, but we have no way to "continue" a specific failed batch if we don't have a `batch_id`.
- **Verification Loop**: We currently don't distinguish between a "Retry" (AI error) and a "Regenerate" (Human preference).
- **Platform Limits**: The `Gemini` generation doesn't currently account for different platform character limits; it treats all platforms as identical text blocks.
