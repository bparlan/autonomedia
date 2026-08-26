# tests/test_ingestion.py

import pytest

from src.autonomedia.ingestion.content_ingestor import capture_content_idea


def test_capture_content_idea_success():
    idea = "This is a test idea."
    result = capture_content_idea(idea)
    assert result["original_idea"] == idea
    assert result["processed_idea"] == idea.strip()
    assert "timestamp" in result

def test_capture_content_idea_empty():
    with pytest.raises(ValueError, match="Content idea cannot be empty."):
        capture_content_idea("")

def test_capture_content_idea_whitespace():
    idea = "   \n   Another idea with whitespace   \n   "
    result = capture_content_idea(idea)
    assert result["original_idea"] == idea
    assert result["processed_idea"] == "Another idea with whitespace"
