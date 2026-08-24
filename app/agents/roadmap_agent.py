from typing import Optional, Dict, Any, Union
from app.llm.ollama_client import OllamaClient
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.prompts.roadmap_prompt import RoadmapPromptBuilder
from app.agents.roadmap_validator import RoadmapValidator, RoadmapValidationError
from app.utils.json_parser import JSONParser
from app.schemas.agent import FeedbackAnalysis
from app.utils.logger import logger


class RoadmapAgent:
    """
    AI Roadmap Generator Agent using local Ollama llama3.1 model.
    Converts analyzed feedback into concrete developer task lists with taxonomy validation
    and automatic self-correction retries. Independent of database access.
    """

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        engine: Optional[TaxonomyEngine] = None,
        validator: Optional[RoadmapValidator] = None,
        prompt_builder: Optional[RoadmapPromptBuilder] = None,
        max_retries: int = 2
    ):
        self.engine = engine or TaxonomyEngine()
        self.client = client or OllamaClient()
        self.validator = validator or RoadmapValidator(self.engine)
        self.prompt_builder = prompt_builder or RoadmapPromptBuilder(self.engine)
        self.max_retries = max_retries

    def generate_roadmap(
        self,
        analysis: Union[FeedbackAnalysis, Dict[str, Any]],
        feedback_text: str
    ) -> Dict[str, Any]:
        """
        Generates a validated developer roadmap dict based on feedback analysis.
        Falls back to rule-based roadmap construction if Ollama connection fails in cloud environments.
        """
        analysis_data = analysis.model_dump() if isinstance(analysis, FeedbackAnalysis) else analysis
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(analysis_data, feedback_text)

        current_prompt = user_prompt
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"RoadmapAgent generating developer roadmap (Attempt {attempt}/{self.max_retries})")
                raw_response = self.client.generate(current_prompt, system_prompt=system_prompt)

                # Parse JSON
                parsed_roadmap = JSONParser.parse(raw_response)

                # Validate against taxonomy & structural rules
                self.validator.validate(parsed_roadmap)

                logger.info(
                    f"RoadmapAgent successfully generated valid roadmap '{parsed_roadmap.get('title')}' "
                    f"with {len(parsed_roadmap.get('tasks', []))} tasks."
                )
                return parsed_roadmap

            except (ValueError, RoadmapValidationError) as err:
                last_error = err
                error_msg = str(err)
                logger.warning(f"RoadmapAgent attempt {attempt} failed validation: {error_msg}")

                if attempt < self.max_retries:
                    current_prompt = (
                        f"{user_prompt}\n\n"
                        f"YOUR PREVIOUS ROADMAP RESPONSE HAD VALIDATION ERRORS:\n{error_msg}\n\n"
                        f"Please fix the errors and return ONLY the corrected valid JSON roadmap object:"
                    )
            except Exception as err:
                logger.warning(f"RoadmapAgent encountered connection/generation exception with Ollama: {err}. Falling back to rule-based roadmap creation.")
                return self._heuristic_fallback(analysis_data, feedback_text)

        logger.warning(f"RoadmapAgent failed validation after {self.max_retries} attempts: {last_error}. Using heuristic fallback.")
        return self._heuristic_fallback(analysis_data, feedback_text)

    def _heuristic_fallback(self, analysis_data: Dict[str, Any], feedback_text: str) -> Dict[str, Any]:
        """Heuristic rule-based roadmap fallback when Ollama is unreachable."""
        category = analysis_data.get("category", "General")
        subcategory = analysis_data.get("subcategory", "System Issue")
        prio = analysis_data.get("priority", "P2")
        title = f"Resolve {category} - {subcategory}"

        return {
            "title": title,
            "description": f"Developer roadmap generated to address user feedback: {feedback_text[:150]}",
            "status": "Planned",
            "effort": "M",
            "progress": 0,
            "tasks": [
                {
                    "title": f"Investigate root cause in {category} ({subcategory})",
                    "description": f"Reproduce reported behavior and trace component logs: {feedback_text[:100]}",
                    "effort": "S",
                    "priority": prio,
                    "progress": 0,
                    "acceptance_criteria": [
                        "Issue reproduced in test environment",
                        "Root cause documented with stack trace"
                    ]
                },
                {
                    "title": f"Develop fix and unit tests for {subcategory}",
                    "description": "Implement bug fix or feature enhancement and verify code coverage.",
                    "effort": "M",
                    "priority": prio,
                    "progress": 0,
                    "acceptance_criteria": [
                        "Code changes merged into main branch",
                        "Automated unit tests pass successfully"
                    ]
                }
            ]
        }
