# UI Module

Status: `in_progress` (server-rendered UI currently embedded in `api/routers/ui.py`)

## Responsibility
- Provide operator-facing interface for chat and document ingestion.
- Expose filters (`domain`, `lang`, `top_k`) with clear UX.
- Display conversation history, confidence feedback, and source snippets.
- Support document deletion and ingestion status feedback.

## Current Implementation
- HTML/CSS/JS are served inline from FastAPI route `/`.
- No build step required (Docker-first, lightweight deployment).

## Future Split (optional)
- `templates/`: HTML templates
- `static/css/`: stylesheets
- `static/js/`: UI logic modules

This split can be done later without changing API endpoints.
