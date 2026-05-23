# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- BrowserProvider for centralized session/artifact lifecycle management
- Platform Registry pattern in worker orchestrator
- Centralized configuration settings

### Changed
- Refactored Mastodon task handler to use BrowserProvider
- Removed unused browser/session/stealth subdirectories
- Refactored core/worker.py routing

### Fixed
- Failure artifact (screenshot) capturing on exception
## [0.5.0] — 2026-05-23

### Added
- Persistent Playwright browser sessions for Mastodon publishing
- Compose automation with post verification loop
- Screenshot observability for debugging
- Runtime/profile isolation for worker-oriented execution

### Architecture
- Runtime state moved outside `src/`
- Human-approved git workflow enforced
- Worker-oriented execution model introduced

### Known Issues
- Selector fragility in Playwright automation
- No retry queue for failed posts
- No structured persistence layer

## [0.4.0] — 2026-05-22

### Added
- persistent Mastodon browser profiles
- autonomous post publishing
- screenshot verification pipeline
- structured worker runtime

### Fixed
- deterministic filesystem path resolution

### Architecture
- migrated to src-layout
- established observability layer
