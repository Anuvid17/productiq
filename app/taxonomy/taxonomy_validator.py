from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.taxonomy.taxonomy_engine import TaxonomyEngine


@dataclass
class TaxonomyValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)


    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False


class TaxonomyValidationError(Exception):
    """Raised when LLM output or dictionary payload violates taxonomy rules."""

    def __init__(self, errors: List[str] | str):
        if isinstance(errors, list):
            self.errors = errors
            super().__init__("; ".join(errors))
        else:
            self.errors = [errors]
            super().__init__(errors)


class TaxonomyValidator:
    """
    Validates dictionary payloads against taxonomy rules and relationships.
    Collects all validation errors instead of failing on the first error.
    """

    def __init__(self, engine: TaxonomyEngine):
        self.engine = engine
        self.taxonomy = engine.get_taxonomy()

        self.feedback_types = set(x.lower() for x in engine.get_feedback_types())
        self.categories = set(x.lower() for x in engine.get_categories())
        self.bug_categories = set(x.lower() for x in engine.get_bug_categories())
        self.severities = set(x.lower() for x in engine.get_severity_levels())
        self.priorities = set(x.lower() for x in engine.get_priority_levels())
        self.impact_areas = set(x.lower() for x in engine.get_impact_areas())
        self.platforms = set(x.lower() for x in engine.get_platforms())
        self.actions = set(x.lower() for x in engine.get_agent_actions())
        self.confidence = set(x.lower() for x in engine.get_confidence_levels())
        self.trend_labels = set(x.lower() for x in engine.get_trend_labels())
        self.roadmap_statuses = set(x.lower() for x in engine.get_roadmap_statuses())
        self.effort_levels = set(x.lower() for x in engine.get_effort_levels())
        self.status_values = set(x.lower() for x in engine.get_status_values())

    def _normalize(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()

    def validate_structured(self, result: dict) -> TaxonomyValidationResult:
        """
        Validates dictionary payload and returns a structured TaxonomyValidationResult
        containing all detected errors.
        """
        vr = TaxonomyValidationResult(is_valid=True, errors=[])

        # 1. Feedback Type
        if "feedback_type" in result:
            ft = self._normalize(result["feedback_type"])
            if ft not in self.feedback_types:
                vr.add_error(f"Invalid feedback_type '{result['feedback_type']}'.")

        # 2. Severity
        if "severity" in result:
            sev = self._normalize(result["severity"])
            if sev not in self.severities:
                vr.add_error(f"Invalid severity '{result['severity']}'.")

        # 3. Priority
        if "priority" in result:
            prio = self._normalize(result["priority"])
            if prio not in self.priorities:
                vr.add_error(f"Invalid priority '{result['priority']}'.")

        # 4. Impact Area
        if "impact_area" in result:
            imp = self._normalize(result["impact_area"])
            if imp not in self.impact_areas:
                vr.add_error(f"Invalid impact_area '{result['impact_area']}'.")

        # 5. Platform
        if "platform" in result:
            plat = self._normalize(result["platform"])
            if plat not in self.platforms:
                vr.add_error(f"Invalid platform '{result['platform']}'.")

        # 6. Recommended Action
        action_val = result.get("recommended_action") or result.get("agent_action")
        if action_val is not None:
            act = self._normalize(action_val)
            if act not in self.actions:
                vr.add_error(f"Invalid recommended_action '{action_val}'.")

        # 7. Confidence
        if "confidence" in result:
            conf = self._normalize(result["confidence"])
            if conf not in self.confidence:
                vr.add_error(f"Invalid confidence '{result['confidence']}'.")

        # 8. Bug Category
        if "bug_category" in result and result["bug_category"]:
            bc = self._normalize(result["bug_category"])
            if bc not in self.bug_categories:
                vr.add_error(f"Invalid bug_category '{result['bug_category']}'.")

        # 9. Category & Subcategory Relationships
        cat_raw = result.get("category")
        sub_raw = result.get("subcategory")

        if cat_raw is not None:
            cat_norm = self._normalize(cat_raw)
            if cat_norm not in self.categories:
                vr.add_error(f"Unknown category '{cat_raw}'.")
            elif sub_raw is not None:
                sub_norm = self._normalize(sub_raw)
                allowed_subs = [
                    s.lower() for s in self.engine.get_subcategories(str(cat_raw))
                ]
                if sub_norm not in allowed_subs:
                    vr.add_error(
                        f"Subcategory '{sub_raw}' does not belong to category '{cat_raw}'."
                    )

        # 10. Optional Trend
        if "trend" in result and result["trend"]:
            tr = self._normalize(result["trend"])
            if tr not in self.trend_labels:
                vr.add_error(f"Invalid trend '{result['trend']}'.")

        # 11. Optional Roadmap Status
        if "roadmap_status" in result and result["roadmap_status"]:
            rms = self._normalize(result["roadmap_status"])
            if rms not in self.roadmap_statuses:
                vr.add_error(f"Invalid roadmap_status '{result['roadmap_status']}'.")

        # 12. Optional Effort
        if "effort" in result and result["effort"]:
            eff = self._normalize(result["effort"])
            if eff not in self.effort_levels:
                vr.add_error(f"Invalid effort '{result['effort']}'.")

        # 13. Optional Feedback Status
        if "status" in result and result["status"]:
            st = self._normalize(result["status"])
            if st not in self.status_values:
                vr.add_error(f"Invalid status '{result['status']}'.")

        return vr

    def validate(self, result: dict) -> bool:
        """
        Validates dictionary payload.
        Raises TaxonomyValidationError with all collected error messages if invalid.
        Returns True if valid.
        """
        vr = self.validate_structured(result)
        if not vr.is_valid:
            raise TaxonomyValidationError(vr.errors)
        return True