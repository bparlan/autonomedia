# tests/test_ai_analysis.py

import json

import pytest

from src.autonomedia.ai.analysis import perform_ai_analysis


# Mocking the DatabaseClient for AnalysisStorage tests
class MockDatabaseClient:
    def __init__(self):
        self.saved_data = None

    async def get_pool(self):
        mock_pool = MockPool()
        return mock_pool

class MockPool:
    async def execute(self, query, *args):
        

# Monkeypatching to use mocks for testing
@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    # Patch AnalysisStorage's DatabaseClient to use our mock.
    monkeypatch.setattr(
        'src.autonomedia.core.storage.analysis_storage', 
        'DatabaseClient', 
        MockDatabaseClient
    )

def test_perform_ai_analysis_success(mock_dependencies):
    content_idea = {"processed_idea": "Hello #world, check out @autonomedia!", "original_idea": "Hello world"}
    
    expected_analysis_data = {
        "original_idea_processed": "Hello #world, check out @autonomedia!",
        "analysis": {
            "keywords": ["hello", "world", "check", "autonomedia"],
            "hashtags": ["#world"],
            "handles": ["@autonomedia!"],
            "visibility_tips": ["Consider using more specific keywords.", "Add a relevant call to action."]
        }
    }
    
    returned_json = perform_ai_analysis(content_idea)
    result_data = json.loads(returned_json)
    
    assert result_data == expected_analysis_data

def test_perform_ai_analysis_empty_idea(mock_dependencies):
    content_idea = {"processed_idea": "", "original_idea": ""}
    
    with pytest.raises(ValueError, match="No processed idea found in content_idea."):
        perform_ai_analysis(content_idea)

def test_perform_ai_analysis_no_entities(mock_dependencies):
    content_idea = {"processed_idea": "just some plain text", "original_idea": "just some plain text"}
    expected_analysis_data = {
        "original_idea_processed": "just some plain text",
        "analysis": {
            "keywords": [],
            "hashtags": [],
            "handles": [],
            "visibility_tips": ["Consider using more specific keywords.", "Add a relevant call to action."]
        }
    }
    
    returned_json = perform_ai_analysis(content_idea)
    result_data = json.loads(returned_json)
    
    assert result_data == expected_analysis_data

def test_perform_ai_analysis_with_mentions_and_hashtags(mock_dependencies):
    content_idea = {"processed_idea": "Great work by @team on #AwesomeProject!", "original_idea": "Great work by @team on #AwesomeProject!"}
    expected_analysis_data = {
        "original_idea_processed": "Great work by @team on #AwesomeProject!",
        "analysis": {
            "keywords": ["great", "work", "team", "awesomeproject"],
            "hashtags": ["#AwesomeProject!"],
            "handles": ["@team"],
            "visibility_tips": ["Consider using more specific keywords.", "Add a relevant call to action."]
        }
    }
    
    returned_json = perform_ai_analysis(content_idea)
    result_data = json.dumps(json.loads(returned_json), indent=4)
    expected_json = json.dumps(expected_analysis_data, indent=4)
    
    assert result_data == expected_json
