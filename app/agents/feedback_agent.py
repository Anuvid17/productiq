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
        Falls back to rule-based taxonomy classification if Ollama connection fails in cloud environments.
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
                    current_prompt = (
                        f"{user_prompt}\n\n"
                        f"YOUR PREVIOUS RESPONSE HAD VALIDATION ERRORS:\n{error_msg}\n\n"
                        f"Please fix the errors and return ONLY the corrected valid JSON object:"
                    )
            except Exception as err:
                logger.warning(f"FeedbackAgent encountered connection/generation exception with Ollama: {err}. Falling back to rule-based taxonomy classification.")
                return self._heuristic_fallback(user_text, platform)

        logger.warning(f"FeedbackAgent failed LLM validation after {self.max_retries} attempts: {last_error}. Using heuristic fallback.")
        return self._heuristic_fallback(user_text, platform)

    def _heuristic_fallback(self, user_text: str, platform: Optional[str] = None) -> FeedbackAnalysis:
        """Heuristic rule-based taxonomy fallback when Ollama is unreachable."""
        lower_text = user_text.lower()
        
        # Determine feedback type
        if any(w in lower_text for w in ["bug", "crash", "error", "fail", "freeze", "hang", "broken", "issue", "cannot", "can't", "slow", "glitch"]):
            feedback_type = "Bug Report"
        elif any(w in lower_text for w in ["add", "feature", "would be great", "please allow", "request", "support", "want", "option"]):
            feedback_type = "Feature Request"
        else:
            feedback_type = "General Feedback"

        # Category & Subcategory
        if any(w in lower_text for w in ["login", "signin", "sign in", "auth", "password", "session", "logout"]):
            category = "Authentication"
            subcategory = "Login"
        elif any(w in lower_text for w in ["bill", "pay", "invoice", "subscr", "card", "plan"]):
            category = "Billing & Subscription"
            subcategory = "Payments"
        elif any(w in lower_text for w in ["slow", "load", "latency", "lag", "cpu", "memory", "perf"]):
            category = "Performance"
            subcategory = "Slow Loading"
        elif any(w in lower_text for w in ["search", "filter", "sort"]):
            category = "Search & Filter"
            subcategory = "Search"
        elif any(w in lower_text for w in ["api", "webhook", "graphql", "oauth", "rest"]):
            category = "API & Integrations"
            subcategory = "REST API"
        else:
            category = "Authentication"
            subcategory = "Login"

        is_bug = (feedback_type == "Bug Report")
        bug_cat = "Functional Bug" if is_bug else "N/A"
        sev = "Critical" if any(w in lower_text for w in ["freeze", "crash", "fatal", "lock", "blocker"]) else "Major"
        prio = "P1" if sev == "Critical" else "P2"
        plt = platform or "Web"
        action = "CREATE_BUG" if is_bug else "CREATE_FEATURE"

        summary = user_text[:80] + "..." if len(user_text) > 80 else user_text

        return FeedbackAnalysis(
            summary=summary,
            feedback_type=feedback_type,
            category=category,
            subcategory=subcategory,
            bug_category=bug_cat,
            severity=sev,
            priority=prio,
            impact_area="All Users",
            platform=plt,
            recommended_action=action,
            confidence="Medium",
            reasoning="Rule-based heuristic fallback applied due to Ollama connection status."
        )
