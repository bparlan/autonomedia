
# Milestone 2: Platform Profiles & User Selection

## Goal
Define platform-specific content requirements and allow users to select platforms via checkboxes.

## Description
This milestone focuses on establishing the system's understanding of different social media platforms' requirements and providing users with a way to choose which platforms they want to target for content adaptation.

## Key Tasks
    - Define standardized platform profiles, including requirements such as character limits, tone, preferred styles, hashtag conventions, and available tagging mechanisms for each potential platform. Ensure these profiles are stored in a consistent format (e.g., JSON or YAML) for easy parsing and management.
    - Implement a user interface component that displays platform logos and allows users to select target platforms using checkboxes.
    - Design the structure for storing platform profiles, utilizing the established `browser/profiles/` directory with platform-specific subdirectories (e.g., `x/`, `linkedin/`, `mastodon/`, `bluesky/`, `threads/`, `facebook/`) to ensure isolated and persistent browser states.
    - *Future Consideration*: Placeholder for developing "Platform Management" functionality to add new platforms and refresh problematic connections/sessions.

## Autonomedia Integration & Advice
    - **Existing Capabilities**: Autonomedia's modular design, browser-first approach, and UI framework facilitate the definition of platform profiles. The recently established `browser/profiles/` directory structure provides a standardized location for platform-specific configurations. This infrastructure supports input handling and AI agent execution via `task` and `agent` tools, leveraging modules like `src/autonomedia/ai/rewriting/gemini.py` and `src/autonomedia/ai/rewriting/context.py`.
    - **Advice**: Standardize the format for platform profiles (e.g., JSON, YAML) to ensure consistency and ease of parsing. Ensure the UI for platform selection is intuitive and integrates smoothly with the chosen UI framework. Furthermore, AI analysis results for these profiles should be structured consistently, preferably in JSON, for seamless integration with other modules like content drafting, aligning with the patterns established in Milestone 1. Platform management logic should be robust for connection stability.
