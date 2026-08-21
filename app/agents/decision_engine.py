from typing import Optional, Dict, Any
from app.schemas.agent import FeedbackAnalysis
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_mapper import TaxonomyMapper
from app.constants import (
    DEFAULT_PLATFORM,
    DEFAULT_BUG_CATEGORY,
    DEFAULT_CONFIDENCE,
    DEFAULT_ACTION,
    DEFAULT_IMPACT,
    UNKNOWN
)


class DecisionEngine:
    """
    Evaluates validated FeedbackAnalysis outputs, applies taxonomy ID mappings,
    enforces business defaults, and produces clean database-ready records.
    """

    def __init__(self, engine: Optional[TaxonomyEngine] = None, mapper: Optional[TaxonomyMapper] = None):
        self.engine = engine or TaxonomyEngine()
        self.mapper = mapper or TaxonomyMapper(self.engine)

    def process(self, analysis: FeedbackAnalysis, input_platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Process FeedbackAnalysis schema object and resolve taxonomy IDs and fallback rules.
        """
        # Resolve platform fallback
        platform = analysis.platform or input_platform or DEFAULT_PLATFORM
        if not self.engine.is_valid_platform(platform):
            platform = DEFAULT_PLATFORM

        # Resolve bug category fallback
        bug_category = analysis.bug_category
        if analysis.feedback_type == "Bug Report" and (not bug_category or bug_category == "N/A"):
            bug_category = DEFAULT_BUG_CATEGORY
        elif analysis.feedback_type != "Bug Report":
            bug_category = "N/A"

        # Resolve taxonomy IDs using mapper
        feedback_type_id = self.mapper.feedback_type_to_id(analysis.feedback_type)
        category_id = self.mapper.category_to_id(analysis.category)
        subcategory_id = self.mapper.subcategory_to_id(analysis.subcategory)

        # Priority score logic / rule override if Critical / Blocker
        priority = analysis.priority
        severity = analysis.severity
        if severity in ["Blocker", "Critical"] and priority in ["P2", "P3"]:
            priority = "P0"  # Automatically promote blocker/critical bugs to P0

        return {
            "summary": analysis.summary,
            "feedback_type": analysis.feedback_type,
            "feedback_type_id": feedback_type_id,
            "category": analysis.category,
            "category_id": category_id,
            "subcategory": analysis.subcategory,
            "subcategory_id": subcategory_id,
            "bug_category": bug_category,
            "severity": severity,
            "priority": priority,
            "impact_area": analysis.impact_area or DEFAULT_IMPACT,
            "platform": platform,
            "recommended_action": analysis.recommended_action or DEFAULT_ACTION,
            "confidence": analysis.confidence or DEFAULT_CONFIDENCE,
            "reasoning": analysis.reasoning,
            "needs_more_information": analysis.needs_more_information or False
        }
