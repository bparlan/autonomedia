# AI Rewrite Flow Documentation

## Overview
The Autonomedia AI rewrite pipeline is deterministic, context-aware, and structured. 

## Flow
1. **Input**: A `RewriteContext` object containing the `source_idea`, `tags`, `mentions`, and `platform`.
2. **Serialization**: The context is serialized into a standard prompt block using `RewriteContext.to_prompt_block()`.
3. **Generation**: The `RewriteProvider` uses this structured block to generate the content.
4. **Normalization**: The raw output is post-processed by `EntityNormalizer` to ensure mention handles are platform-compliant.
5. **Validation**: The final content is checked against platform limits by the `ModerationAdapter`.

## Context Schema
The `RewriteContext` dataclass ensures that all necessary variables are passed to the AI consistently.

- `source_idea`: The core message.
- `tags`: List of relevant hashtags.
- `mentions`: List of normalized entity identifiers.
- `url`: Optional canonical URL.
- `platform`: Target platform (influences style and constraints).
