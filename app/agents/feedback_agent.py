from typing import Optional, Dict, Any
from app.llm.ollama_client import OllamaClient
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_validator import TaxonomyValidator, TaxonomyValidationError
from app.prompts.feedback_prompt import FeedbackPromptBuilder
from app.utils.json_parser import JSONParser
from app.schemas.agent import FeedbackAnalysis
from app.utils.logger import logger


class FeedbackAgent:
    """
    Structured AI Feedback Agent using local Ollama llama3.1 model.
    Enforces system prompt taxonomy instructions, JSON extraction, taxonomy validation,
    and automatic self-correction retries.
    """

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        engine: Optional[TaxonomyEngine] = None,
        validator: Optional[TaxonomyValidator] = None,
        prompt_builder: Optional[FeedbackPromptBuilder] = None,
        max_retries: int = 2
    ):
        self.engine = engine or TaxonomyEngine()
        self.client = client or OllamaClient()
        self.validator = validator or TaxonomyValidator(self.engine)
        self.prompt_builder = prompt_builder or FeedbackPromptBuilder(self.engine)
        self.max_retries = max_retries

    def analyze(self, user_text: str, platform: Optional[str] = None) -> FeedbackAnalysis:
        """
        Analyzes raw customer feedback and returns a validated FeedbackAnalysis Pydantic model.
        """
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(user_text, platform)

        current_prompt = user_prompt
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"FeedbackAgent analyzing input (Attempt {attempt}/{self.max_retries})")
                raw_response = self.client.generate(current_prompt, system_prompt=system_prompt)

                # Parse JSON
                parsed_data = JSONParser.parse(raw_response)

                # Validate against taxonomy
                self.validator.validate(parsed_data)

                # Construct Pydantic model
                analysis = FeedbackAnalysis(**parsed_data)
                logger.info(f"FeedbackAgent successfully classified feedback: {analysis.feedback_type} -> {analysis.category} / {analysis.subcategory}")
                return analysis

            except (ValueError, TaxonomyValidationError) as err:
                last_error = err
                error_msg = str(err)
                logger.warning(f"FeedbackAgent attempt {attempt} failed validation: {error_msg}")

                if attempt < self.max_retries:
                    # Construct self-correction retry prompt
                    current_prompt = (
                        f"{user_prompt}\n\n"
                        f"YOUR PREVIOUS RESPONSE HAD VALIDATION ERRORS:\n{error_msg}\n\n"
                        f"Please fix the errors and return ONLY the corrected valid JSON object:"
                    )

        logger.error(f"FeedbackAgent failed classification after {self.max_retries} attempts.")
        raise ValueError(f"FeedbackAgent failed taxonomy validation: {last_error}") from last_error
