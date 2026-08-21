import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional, Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TAXONOMY_PATH = BASE_DIR / "taxonomy.json"


@lru_cache(maxsize=1)
def _load_raw_taxonomy(path_str: str) -> dict:
    """
    Module-level cached loader for taxonomy JSON data.
    """
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Taxonomy file not found at: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


class TaxonomyEngine:
    """
    Loads taxonomy.json and provides indexed, O(1) lookup helper methods.
    """

    def __init__(self, taxonomy_path: Optional[Path | str] = None):
        if taxonomy_path:
            self.taxonomy_path = Path(taxonomy_path).resolve()
            with open(self.taxonomy_path, "r", encoding="utf-8") as file:
                self.taxonomy = json.load(file)
        else:
            self.taxonomy_path = DEFAULT_TAXONOMY_PATH
            self.taxonomy = _load_raw_taxonomy(str(self.taxonomy_path))

        self.category_by_name: Dict[str, dict] = {}
        self.category_by_id: Dict[str, dict] = {}
        self.subcategory_by_name: Dict[str, dict] = {}
        self.subcategory_to_parent: Dict[str, str] = {}
        self.feedback_type_by_name: Dict[str, dict] = {}
        self.feedback_type_by_id: Dict[str, dict] = {}

        self._build_indexes()

    def _build_indexes(self) -> None:
        """
        Build O(1) dictionary indexes for categories, subcategories, and feedback types.
        """
        self.category_by_name.clear()
        self.category_by_id.clear()
        self.subcategory_by_name.clear()
        self.subcategory_to_parent.clear()
        self.feedback_type_by_name.clear()
        self.feedback_type_by_id.clear()

        for ft in self.taxonomy.get("feedback_types", []):
            if "name" in ft:
                self.feedback_type_by_name[ft["name"].lower()] = ft
            if "id" in ft:
                self.feedback_type_by_id[ft["id"]] = ft

        for cat in self.taxonomy.get("categories", []):
            cat_name = cat.get("name", "")
            cat_id = cat.get("id", "")
            if cat_name:
                self.category_by_name[cat_name.lower()] = cat
            if cat_id:
                self.category_by_id[cat_id] = cat

            for sub in cat.get("subcategories", []):
                sub_name = sub.get("name", "")
                if sub_name:
                    self.subcategory_by_name[sub_name.lower()] = sub
                    self.subcategory_to_parent[sub_name.lower()] = cat_name

    def get_taxonomy(self) -> dict:
        return self.taxonomy

    def get_feedback_types(self) -> List[str]:
        return [x["name"] for x in self.taxonomy.get("feedback_types", [])]

    def get_categories(self) -> List[str]:
        return [x["name"] for x in self.taxonomy.get("categories", [])]

    def get_subcategories(self, category_name: str) -> List[str]:
        cat = self.get_category(category_name)
        if cat:
            return [sub["name"] for sub in cat.get("subcategories", [])]
        return []

    def get_category(self, category_name: str) -> Optional[dict]:
        if not category_name:
            return None
        return self.category_by_name.get(category_name.lower())

    def get_parent_category(self, subcategory_name: str) -> Optional[str]:
        if not subcategory_name:
            return None
        return self.subcategory_to_parent.get(subcategory_name.lower())

    def get_bug_categories(self) -> List[str]:
        return self.taxonomy.get("bug_categories", [])

    def get_severity_levels(self) -> List[str]:
        return self.taxonomy.get("severity_levels", [])

    def get_priority_levels(self) -> List[str]:
        return self.taxonomy.get("priority_levels", [])

    def get_impact_areas(self) -> List[str]:
        return self.taxonomy.get("impact_areas", [])

    def get_platforms(self) -> List[str]:
        return self.taxonomy.get("platforms", [])

    def get_agent_actions(self) -> List[str]:
        return self.taxonomy.get("agent_actions", [])

    def get_actions(self) -> List[str]:
        return self.get_agent_actions()

    def get_confidence_bands(self) -> List[str]:
        return self.taxonomy.get("confidence_levels", [])

    def get_confidence_levels(self) -> List[str]:
        return self.get_confidence_bands()

    def get_trend_labels(self) -> List[str]:
        return self.taxonomy.get("trend_labels", ["Rising", "Stable", "Declining", "New"])

    def get_roadmap_statuses(self) -> List[str]:
        return self.taxonomy.get("roadmap_status", [])

    def get_roadmap_status(self) -> List[str]:
        return self.get_roadmap_statuses()

    def get_effort_levels(self) -> List[str]:
        return self.taxonomy.get("effort_levels", ["XS", "S", "M", "L", "XL"])

    def get_status_values(self) -> List[str]:
        return self.taxonomy.get("status_values", ["New", "Triaged", "Linked", "Resolved"])

    def get_task_statuses(self) -> List[str]:
        return self.taxonomy.get("task_statuses", ["Open", "In Review", "Approved", "In Progress", "Testing", "Resolved", "Closed"])

    # Validation Helpers
    def is_valid_feedback_type(self, value: str) -> bool:
        return bool(value and value.lower() in self.feedback_type_by_name)

    def is_valid_category(self, value: str) -> bool:
        return bool(value and value.lower() in self.category_by_name)

    def is_valid_subcategory(self, category_name: str, subcategory_name: str) -> bool:
        if not category_name or not subcategory_name:
            return False
        parent = self.get_parent_category(subcategory_name)
        return parent is not None and parent.lower() == category_name.lower()

    def is_valid_platform(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_platforms()))

    def is_valid_bug_category(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_bug_categories()))

    def is_valid_severity(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_severity_levels()))

    def is_valid_priority(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_priority_levels()))

    def is_valid_impact(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_impact_areas()))

    def is_valid_action(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_agent_actions()))

    def is_valid_confidence(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_confidence_levels()))

    def is_valid_roadmap_status(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_roadmap_statuses()))

    def is_valid_task_status(self, value: str) -> bool:
        return bool(value and value.lower() in set(x.lower() for x in self.get_task_statuses()))
