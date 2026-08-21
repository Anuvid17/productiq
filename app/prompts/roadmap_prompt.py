from typing import Optional, Dict, Any
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_formatter import TaxonomyFormatter


class RoadmapPromptBuilder:
    """
    Dynamically constructs system and user prompts for local Ollama llama3.1 developer roadmap generation.
    Injects authoritative taxonomy status and effort bounds.
    """

    def __init__(self, engine: Optional[TaxonomyEngine] = None):
        self.engine = engine or TaxonomyEngine()
        self.formatter = TaxonomyFormatter(self.engine)

    def build_system_prompt(self) -> str:
        effort_levels = ", ".join(self.engine.get_effort_levels())
        roadmap_statuses = ", ".join(self.engine.get_roadmap_statuses())

        return f"""You are ProductIQ's Roadmap Generation Agent.
Your job is to convert analyzed product feedback into an actionable, step-by-step technical developer roadmap.

CRITICAL INSTRUCTIONS:
1. Return ONLY a single raw valid JSON object.
2. Do NOT wrap the JSON in Markdown code fences (no ```json or ```).
3. Do NOT output any introductory text, explanation, or notes outside the JSON object.
4. Tasks MUST be concrete, technical, and actionable for developers. Avoid vague tasks like "Fix the bug" or "Test the app".
5. Effort levels MUST be selected ONLY from: [{effort_levels}]
6. Roadmap status MUST be set to "Backlog".
7. Every task MUST have a non-empty list of testable acceptance criteria.
8. Set progress = 0 for the roadmap and 0 for every task.

JSON OUTPUT STRUCTURE SCHEMA:
{{
  "title": "<Short technical title for the roadmap>",
  "description": "<Overview of engineering work required>",
  "status": "Backlog",
  "effort": "<Overall effort: XS, S, M, L, XL>",
  "progress": 0,
  "tasks": [
    {{
      "title": "<Specific technical task name>",
      "description": "<Detailed explanation of engineering implementation steps>",
      "effort": "<Task effort: XS, S, M, L, XL>",
      "status": "Open",
      "progress": 0,
      "dependencies": [],
      "acceptance_criteria": [
        "<Concrete testable acceptance criterion 1>",
        "<Concrete testable acceptance criterion 2>"
      ]
    }}
  ]
}}
"""

    def build_user_prompt(self, analysis_data: Dict[str, Any], feedback_text: str) -> str:
        return f"""ANALYZED FEEDBACK FOR ROADMAP GENERATION:
Feedback Summary: {analysis_data.get('summary')}
Feedback Type: {analysis_data.get('feedback_type')}
Category: {analysis_data.get('category')}
Subcategory: {analysis_data.get('subcategory')}
Severity: {analysis_data.get('severity')}
Priority: {analysis_data.get('priority')}
Platform: {analysis_data.get('platform')}
Original Customer Text:
\"\"\"
{feedback_text.strip()}
\"\"\"

Return JSON developer roadmap now:"""
