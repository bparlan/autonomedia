# Milestone 3: Platform-Specific Content Drafting & Variation Logic

## Goal
Adapt the core content idea into platform-specific drafts and establish the logic for generating content variations.

## Description
This milestone focuses on the AI's ability to tailor content for different platforms based on their unique requirements and to generate slightly modified versions of content for repeated postings.

## Key Tasks
    - Develop AI logic for rewriting the core content idea to adhere to selected platform profiles (e.g., character limits, tone, hashtag usage, handle tagging). Leverage modules like `src/autonomedia/ai/rewriting/gemini.py` for these tasks.
    - Implement the AI logic for generating initial platform-specific drafts.
    - Design and implement the AI logic for automatically generating slight variations of approved drafts for subsequent posts (e.g., rephrasing, synonym use, order changes) while preserving the core message.
    - Integrate an address book-like functionality for managing and retrieving persistent handles/entities across different platforms and their available profiles, potentially using utilities from `src/autonomedia/content/transforms/entity_normalizer.py`.

## Autonomedia Integration & Advice
    - **Existing Capabilities**: Autonomedia's async-native nature, browser-first approach, and LLM integration capabilities, particularly via `task` and `agent` tools as established in Milestone 1, are foundational for AI-driven content adaptation.
    - **Advice**: Ensure AI prompts are precisely crafted for platform-specific rewriting and variation generation, paying close attention to platform constraints and desired tone. The variation logic should be maintained to preserve message integrity. Furthermore, AI-generated content drafts and variations should be structured consistently, preferably in JSON, for seamless integration with other modules. The address book feature should prioritize persistence and efficient lookup for managing handles and entities.
