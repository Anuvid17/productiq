from typing import Optional
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_formatter import TaxonomyFormatter


class FeedbackPromptBuilder:
    """
    Dynamically generates system and user prompts for local Ollama llama3.1 feedback analysis.
    Uses TaxonomyFormatter dynamically to inject authoritative taxonomy bounds.
    """

    def __init__(self, engine: Optional[TaxonomyEngine] = None):
        self.engine = engine or TaxonomyEngine()
        self.formatter = TaxonomyFormatter(self.engine)

    def build_system_prompt(self) -> str:

        taxonomy_text = self.formatter.format()
        return f"""You are ProductIQ's Feedback Analysis Agent.
Your job is to analyze a user's product feedback and classify it according to the official ProductIQ taxonomy.

CRITICAL INSTRUCTIONS:
1. Return ONLY a single raw valid JSON object.
2. Do NOT wrap the JSON in Markdown code fences (no ```json or ```).
3. Do NOT output any introductory text, explanation, or notes outside the JSON object.
4. The taxonomy supplied below is authoritative. You must ONLY use values listed in the taxonomy.
5. Never invent categories, subcategories, severities, priorities, actions, or feedback types outside the taxonomy.
6. The subcategory MUST strictly belong to the chosen parent category.

AUTHORITATIVE SYSTEM TAXONOMY:
{taxonomy_text}

JSON OUTPUT STRUCTURE SCHEMA:
{{
  "summary": "<Concise 1-sentence summary of the user issue/request>",
  "feedback_type": "<Exactly one from FEEDBACK TYPES>",
  "category": "<Exactly one from CATEGORIES>",
  "subcategory": "<Exactly one subcategory belonging to the chosen category>",
  "bug_category": "<Exactly one from BUG CATEGORIES if Bug Report, else 'N/A'>",
  "severity": "<Exactly one from SEVERITY>",
  "priority": "<Exactly one from PRIORITY>",
  "impact_area": "<Exactly one from IMPACT>",
  "platform": "<Exactly one from PLATFORMS>",
  "recommended_action": "<Exactly one from ACTIONS>",
  "confidence": "<Exactly one from CONFIDENCE>",
  "reasoning": "<Short explanation for classification decisions>"
}}
"""

    def build_user_prompt(self, user_text: str, platform: Optional[str] = None) -> str:
        platform_info = f"\nReported Platform: {platform}" if platform else ""
        return f"USER FEEDBACK TO ANALYZE:{platform_info}\n\"\"\"\n{user_text.strip()}\n\"\"\"\n\nReturn JSON now:"
