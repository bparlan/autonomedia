# src/autonomedia/ingestion/content_ingestor.py


def capture_content_idea(idea_text: str) -> dict:
    """Captures a user-provided content idea.

    Args:
        idea_text: The raw content idea provided by the user.

    Returns:
        A dictionary representing the captured content idea, potentially with basic processing.
    """
    if not idea_text:
        raise ValueError("Content idea cannot be empty.")

    # Basic processing: trim whitespace
    processed_idea = idea_text.strip()

    # In a real scenario, this might involve more complex validation or formatting.
    # For now, we return a simple structure.
    return {
        "original_idea": idea_text,
        "processed_idea": processed_idea,
        "timestamp": "some_timestamp",  # Placeholder for actual timestamp generation
    }
