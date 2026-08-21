# src/autonomedia/ai/rewriting/gemini.py


import structlog

from src.autonomedia.ai.analysis import AIAnalysisError
from src.autonomedia.ai.rewriting.base import RewriteProvider
from src.autonomedia.ai.rewriting.context import RewriteContext

logger = structlog.get_logger()


class GeminiProvider(RewriteProvider):
    def __init__(self):
        self.client = GeminiAIClient()


    def _get_platform_char_limit(self, platform: str) -> int:
        """Get character limit for a specific platform."""
        platform_constraints = {
            "linkedin": 3000,
            "x": 280,
            "mastodon": 500,
        }
        return platform_constraints.get(platform.lower(), 280)

    def _get_platform_tone(self, platform: str) -> str:
        """Get tone for a specific platform."""
        platform_constraints = {
            "linkedin": "professional",
            "x": "concise",
            "mastodon": "conversational",
        }
        return platform_constraints.get(platform.lower(), "concise")
    async def rewrite(self, context: RewriteContext, prompt: str) -> str:
        """Rewrites text using Gemini AI client, considering platform specifics.
        
        Args:
            context: The rewrite context containing source_idea and platform
            prompt: The prompt for the AI rewrite
            
        Returns:
            The rewritten content for the platform
            
        Raises:
            AIAnalysisError: If AI analysis fails
        """
        # Validate input
        if not context.source_idea or not context.source_idea.strip():
            error_msg = "Cannot rewrite empty or None content idea"
            logger.error("empty_input", error=error_msg)
            raise AIAnalysisError(error_msg)
        
        # Use AI Analysis to extract keywords, hashtags, handles, etc.
        analysis = self.client.analyze_idea(idea_text=context.source_idea)
        
        # Construct a more platform-aware rewrite prompt
        platform = context.platform.lower()
        platform_constraints = {
            "linkedin": {
                "char_limit": 3000,
                "tone": "professional",
                "hashtags_max": 3,
                "require_title": True
            },
            "x": {
                "char_limit": 280,
                "tone": "concise",
                "hashtags_max": 4,
            },
            "mastodon": {
                "char_limit": 500,
                "tone": "conversational",
                "hashtags_max": 5,
            },
        }
        
        constraints = platform_constraints.get(platform, platform_constraints["x"])  # Default to X if platform unknown
        
        # Build a more detailed prompt for the AI
        generated_rewrite = f"Prompt for AI: Rewrite the following idea for {platform}. "
        generated_rewrite += f"Adhere to a {constraints['tone']} tone and a character limit of {constraints['char_limit']}. "
        if constraints.get('hashtags_max'):
            generated_rewrite += f"Use up to {constraints['hashtags_max']} relevant hashtags. "
        if constraints.get('require_title'):
            generated_rewrite += "Include a concise title. "
        generated_rewrite += f"Original idea: {context.source_idea}"
        
        # Simulate AI rewrite generation based on the enhanced prompt
        # In a real implementation, this would call a sophisticated AI model
        # For now, we'll just return a placeholder based on analysis
        placeholder_rewrite = f"[Platform: {platform.capitalize()}] {context.source_idea}\n\n"  # Simple base
        placeholder_rewrite += f"Analysis results: Keywords: {', '.join(analysis.get('keywords', []))}. "
        placeholder_rewrite += f"Tips: {'. '.join(analysis.get('visibility_tips', []))}"
        
        # Truncate if necessary (basic implementation)
        final_rewrite = placeholder_rewrite[:constraints['char_limit']]
        
        return final_rewrite


class GeminiAIClient:
    def analyze_idea(self, idea_text: str) -> dict:
        """Analyzes a content idea to extract keywords, hashtags, handles, etc.
        
        Args:
            idea_text: The content idea to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not idea_text:
                return {
                    "keywords": [],
                    "hashtags": [],
                    "handles": [],
                    "visibility_tips": [],
                }

            keywords = [w for w in idea_text.lower().split() if len(w) > 4]
            hashtags = [
                f"#{w}" for w in idea_text.split() if w.lower().startswith("#")
            ]
            handles = [
                w for w in idea_text.split() if w.lower().startswith("@")
            ]
            tips = [
                "Use more specific keywords.",
                "Add a call to action.",
            ]

            return {
                "keywords": keywords,
                "hashtags": hashtags,
                "handles": handles,
                "visibility_tips": tips,
            }
        except Exception as e:
            err_msg = f"Error during analysis for '{idea_text[:50]}': {e}"
            raise AIAnalysisError(err_msg) from e
