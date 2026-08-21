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

        logger.error(f"RoadmapAgent failed generation after {self.max_retries} attempts.")
        raise ValueError(f"RoadmapAgent failed validation: {last_error}") from last_error
