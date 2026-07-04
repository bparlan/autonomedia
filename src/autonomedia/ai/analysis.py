# src/autonomedia/ai/analysis.py

import json

from src.autonomedia.ai.rewriting.gemini import GeminiAIClient
from src.autonomedia.core.storage.analysis_storage import AnalysisStorage


class AIAnalysisError(Exception):
    """Custom exception for AI analysis failures."""

    pass


def perform_ai_analysis(content_idea: dict) -> str:
    """Performs AI analysis on a content idea and standardizes the output to JSON.

    Args:
        content_idea: A dictionary containing the content idea, as returned by capture_content_idea.

    Returns:
        A JSON string representing the AI analysis results.

    Raises:
        ValueError: If the processed idea is empty.
        AIAnalysisError: If any error occurs during AI analysis or storage.
    """
    ai_client = GeminiAIClient()
    storage_client = AnalysisStorage()

    original_idea = content_idea.get("processed_idea", "")
    if not original_idea:
        raise ValueError("No processed idea found in content_idea.")

    try:
        analysis_results = ai_client.analyze_idea(original_idea)

        full_analysis = {
            "original_idea_processed": original_idea,
            "analysis": analysis_results,
        }

        storage_client.save_analysis_result(full_analysis)

        return json.dumps(full_analysis, indent=4)

    except Exception as e:
        error_message = f"An error occurred during AI analysis or storage for idea '{original_idea[:50]}': {e}"

        raise AIAnalysisError(error_message) from e
