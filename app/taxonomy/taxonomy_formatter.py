from app.taxonomy.taxonomy_engine import TaxonomyEngine


class TaxonomyFormatter:
    """
    Converts the taxonomy into a clean, human-readable format for LLM system prompts.
    The LLM sees readable names, never internal IDs.
    """

    def __init__(self, engine: TaxonomyEngine):
        self.engine = engine
        self.taxonomy = engine.get_taxonomy()

    def format(self) -> str:
        sections = [
            self._feedback_types(),
            self._categories(),
            self._bug_categories(),
            self._severity_levels(),
            self._priority_levels(),
            self._impact_areas(),
            self._agent_actions(),
            self._confidence_levels(),
            self._roadmap_status(),
            self._effort_levels(),
            self._platforms(),
            self._status_values()
        ]

        return "\n\n".join(sections)

    def _feedback_types(self) -> str:
        lines = ["========== FEEDBACK TYPES =========="]
        for item in self.taxonomy.get("feedback_types", []):
            lines.append(f"- {item['name']}")
        return "\n".join(lines)

    def _categories(self) -> str:
        lines = ["========== CATEGORIES =========="]
        for category in self.taxonomy.get("categories", []):
            lines.append("")
            lines.append(category["name"])
            for sub in category.get("subcategories", []):
                lines.append(f"    • {sub['name']}")
        return "\n".join(lines)

    def _bug_categories(self) -> str:
        lines = ["========== BUG CATEGORIES =========="]
        for bug in self.engine.get_bug_categories():
            lines.append(f"- {bug}")
        return "\n".join(lines)

    def _severity_levels(self) -> str:
        lines = ["========== SEVERITY =========="]
        for item in self.engine.get_severity_levels():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _priority_levels(self) -> str:
        lines = ["========== PRIORITY =========="]
        for item in self.engine.get_priority_levels():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _impact_areas(self) -> str:
        lines = ["========== IMPACT =========="]
        for item in self.engine.get_impact_areas():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _agent_actions(self) -> str:
        lines = ["========== ACTIONS =========="]
        for item in self.engine.get_agent_actions():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _confidence_levels(self) -> str:
        lines = ["========== CONFIDENCE =========="]
        for item in self.engine.get_confidence_levels():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _roadmap_status(self) -> str:
        lines = ["========== ROADMAP STATUS =========="]
        for item in self.engine.get_roadmap_statuses():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _effort_levels(self) -> str:
        lines = ["========== EFFORT =========="]
        for item in self.engine.get_effort_levels():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _platforms(self) -> str:
        lines = ["========== PLATFORMS =========="]
        for item in self.engine.get_platforms():
            lines.append(f"- {item}")
        return "\n".join(lines)

    def _status_values(self) -> str:
        lines = ["========== STATUS =========="]
        for item in self.engine.get_status_values():
            lines.append(f"- {item}")
        return "\n".join(lines)