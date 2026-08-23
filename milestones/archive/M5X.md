# Milestone: M5X - Critical Review Fix Milestone

## Overview
This milestone addresses critical architectural risks and technical debt identified in the Autonomedia codebase. The primary objective is to harden the system's reliability and extensibility, ensuring it adheres to the "CORE ENGINEERING PRINCIPLES" regarding modularity, browser-first architecture, and robust observability.

## Status: COMPLETE

## Roadmap

### 1. Architectural Cleanup
- [x] **Remove Phantom Architecture**: Clean up empty/unused subdirectories in `src/autonomedia/browser/`.
- [x] **Implement Registry Pattern**: Refactor `src/autonomedia/core/worker.py` to use a platform-handler registry instead of hardcoded if/else routing.

### 2. Browser Abstraction
- [x] **Implement BrowserProvider**: Create a centralized `BrowserProvider` in `src/autonomedia/browser/provider.py` (or similar) to handle context management, lifecycle, and consistent profile loading.
- [x] **Unified Failure Context**: Integrate a shared logger and `task_id` into all platform handlers to ensure artifacts (screenshots, logs) are captured before context closure.

### 3. Selector Hardening
- [x] **Audit & Refactor Selectors**: Remove fragile "deep CSS chain" fallbacks. Enforce `Mandatory Selector Rules` (use role/label/text) across all platform implementations (starting with Mastodon).

### 4. Operational Hardening
- [x] **Configuration Centralization**: Migrate hardcoded path configurations (e.g., `BROWSER_DATA_DIR`) to a centralized config utility.

## Integrity Notes
- **Worker Loop**: The core worker loop in `worker.py` remains untouched as per review recommendation.
- **Content Model**: Schema remains stable.
- **Browser Profiles**: Storage strategy remains directory-based.

## Execution Strategy
- Pre-flight snapshot before every `edit`.
- `Read-First` mandate for all touched files.
- `ruff` linting and formatting after each block.
