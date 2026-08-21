from typing import Optional, Dict
from app.taxonomy.taxonomy_engine import TaxonomyEngine


class TaxonomyMapper:
    """
    Maps taxonomy names <-> IDs using the TaxonomyEngine.
    """

    def __init__(self, engine: TaxonomyEngine):
        self.engine = engine
        self.taxonomy = engine.get_taxonomy()

        # Build name <-> ID lookup maps
        self._category_name_to_id: Dict[str, str] = {}
        self._category_id_to_name: Dict[str, str] = {}
        self._subcategory_name_to_id: Dict[str, str] = {}
        self._subcategory_id_to_name: Dict[str, str] = {}
        self._feedback_type_name_to_id: Dict[str, str] = {}
        self._feedback_type_id_to_name: Dict[str, str] = {}

        self._build_maps()

    def _build_maps(self) -> None:
        """
        Build lookup dictionaries from taxonomy engine.
        """
        self._category_name_to_id.clear()
        self._category_id_to_name.clear()
        self._subcategory_name_to_id.clear()
        self._subcategory_id_to_name.clear()
        self._feedback_type_name_to_id.clear()
        self._feedback_type_id_to_name.clear()

        for ft in self.taxonomy.get("feedback_types", []):
            if "name" in ft and "id" in ft:
                self._feedback_type_name_to_id[ft["name"].lower()] = ft["id"]
                self._feedback_type_id_to_name[ft["id"]] = ft["name"]

        for cat in self.taxonomy.get("categories", []):
            cat_name = cat.get("name", "")
            cat_id = cat.get("id", "")
            if cat_name and cat_id:
                self._category_name_to_id[cat_name.lower()] = cat_id
                self._category_id_to_name[cat_id] = cat_name

            for sub in cat.get("subcategories", []):
                sub_name = sub.get("name", "")
                sub_id = sub.get("id", "")
                if sub_name and sub_id:
                    self._subcategory_name_to_id[sub_name.lower()] = sub_id
                    self._subcategory_id_to_name[sub_id] = sub_name

    # CATEGORY LOOKUPS
    def category_to_id(self, category_name: str) -> Optional[str]:
        if not category_name:
            return None
        return self._category_name_to_id.get(category_name.lower())

    def category_name_to_id(self, category_name: str) -> Optional[str]:
        return self.category_to_id(category_name)

    def category_id_to_name(self, category_id: str) -> Optional[str]:
        if not category_id:
            return None
        return self._category_id_to_name.get(category_id)

    # SUBCATEGORY LOOKUPS
    def subcategory_to_id(self, subcategory_name: str) -> Optional[str]:
        if not subcategory_name:
            return None
        return self._subcategory_name_to_id.get(subcategory_name.lower())

    def subcategory_name_to_id(self, subcategory_name: str) -> Optional[str]:
        return self.subcategory_to_id(subcategory_name)

    def subcategory_id_to_name(self, subcategory_id: str) -> Optional[str]:
        if not subcategory_id:
            return None
        return self._subcategory_id_to_name.get(subcategory_id)

    # FEEDBACK TYPE LOOKUPS
    def feedback_type_to_id(self, name: str) -> Optional[str]:
        if not name:
            return None
        return self._feedback_type_name_to_id.get(name.lower())

    def feedback_type_name_to_id(self, name: str) -> Optional[str]:
        return self.feedback_type_to_id(name)

    def feedback_type_id_to_name(self, feedback_id: str) -> Optional[str]:
        if not feedback_id:
            return None
        return self._feedback_type_id_to_name.get(feedback_id)

    # BUG CATEGORY LOOKUPS
    def bug_category_to_id(self, bug_category_name: str) -> Optional[str]:
        """
        Bug categories in taxonomy.json are names only. Returns canonical name or None.
        """
        for bug in self.engine.get_bug_categories():
            if bug.lower() == (bug_category_name or "").lower():
                return bug
        return None

    # PARENT CATEGORY & OBJECT LOOKUPS
    def get_parent_category(self, subcategory_name: str) -> Optional[str]:
        return self.engine.get_parent_category(subcategory_name)

    def get_category_object(self, category_name: str) -> Optional[dict]:
        return self.engine.get_category(category_name)