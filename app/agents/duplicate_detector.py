import re
from typing import List, Optional, Union, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.duplicate import DuplicateCheckResult
from app.utils.logger import logger


class DuplicateDetector:
    """
    Deterministic duplicate feedback detector using TF-IDF text vectorization
    and Cosine Similarity. Does NOT use LLMs or vector databases.
    Independent of direct database operations.
    """

    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r"\blog\s+in\b", "login", text)
        text = re.sub(r"\bsign\s+in\b", "signin", text)
        text = re.sub(r"\blog\s+out\b", "logout", text)
        text = re.sub(r"\bsign\s+out\b", "signout", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def detect(
        self,
        new_text: str,
        candidate_records: List[Union[Any, Dict[str, Any]]],
        new_metadata: Optional[Dict[str, Any]] = None
    ) -> DuplicateCheckResult:
        """
        Compares new_text against candidate_records and returns DuplicateCheckResult.
        """
        normalized_new = self._normalize_text(new_text)

        if not normalized_new or not candidate_records:
            return DuplicateCheckResult(
                is_duplicate=False,
                similarity_score=0.0,
                matched_feedback_id=None,
                matched_text=None,
                reason="No candidate records or empty input text provided for comparison."
            )

        # Prepare text list for TF-IDF
        candidate_texts = []
        valid_candidates = []

        for item in candidate_records:
            item_text = getattr(item, "original_text", None) or (item.get("original_text") if isinstance(item, dict) else None)
            norm_item = self._normalize_text(item_text or "")
            if norm_item:
                candidate_texts.append(norm_item)
                valid_candidates.append(item)

        if not candidate_texts:
            return DuplicateCheckResult(
                is_duplicate=False,
                similarity_score=0.0,
                matched_feedback_id=None,
                matched_text=None,
                reason="No valid candidate text records found."
            )

        corpus = [normalized_new] + candidate_texts
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), stop_words="english", sublinear_tf=True)
        try:

            tfidf_matrix = vectorizer.fit_transform(corpus)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except ValueError:
            return DuplicateCheckResult(
                is_duplicate=False,
                similarity_score=0.0,
                matched_feedback_id=None,
                matched_text=None,
                reason="TF-IDF vectorization failed due to empty vocabulary."
            )

        best_score = 0.0
        best_candidate = None

        stopwords = {
            "i", "me", "my", "myself", "we", "our", "ours", "you", "your", "he", "him", "she", "her",
            "it", "its", "they", "them", "what", "which", "who", "whom", "this", "that", "these",
            "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or",
            "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against",
            "between", "into", "through", "during", "before", "after", "above", "below", "to", "from",
            "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once",
            "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
            "can", "will", "just", "should", "now"
        }
        new_words = set(normalized_new.split()) - stopwords

        for idx, score in enumerate(similarities):
            candidate = valid_candidates[idx]
            cand_text = candidate_texts[idx]
            tfidf_score = float(score)

            cand_words = set(cand_text.split()) - stopwords
            dice_score = 0.0
            if new_words and cand_words:
                overlap = new_words & cand_words
                dice_score = (2.0 * len(overlap)) / (len(new_words) + len(cand_words))

            cand_score = max(tfidf_score, dice_score)

            # Metadata taxonomy boost if metadata available
            if new_metadata:
                cand_category = getattr(candidate, "category", None) or (candidate.get("category") if isinstance(candidate, dict) else None)
                cand_sub = getattr(candidate, "subcategory", None) or (candidate.get("subcategory") if isinstance(candidate, dict) else None)
                new_cat = new_metadata.get("category")
                new_sub = new_metadata.get("subcategory")

                if new_cat and cand_category and new_cat.lower() == cand_category.lower():
                    cand_score += 0.05
                if new_sub and cand_sub and new_sub.lower() == cand_sub.lower():
                    cand_score += 0.05

            if cand_score > best_score:
                best_score = cand_score
                best_candidate = candidate

        best_score = min(round(best_score, 4), 1.0)
        is_dup = best_score >= self.threshold

        if is_dup and best_candidate:
            candidate_id = str(getattr(best_candidate, "id", None) or (best_candidate.get("id") if isinstance(best_candidate, dict) else ""))
            cand_orig_text = getattr(best_candidate, "original_text", None) or (best_candidate.get("original_text") if isinstance(best_candidate, dict) else "")
            logger.info(f"DuplicateDetector found match [ID: {candidate_id}, score: {best_score}]")
            return DuplicateCheckResult(
                is_duplicate=True,
                similarity_score=best_score,
                matched_feedback_id=candidate_id,
                matched_text=cand_orig_text,
                reason=f"High textual similarity ({best_score:.2f}) meeting threshold ({self.threshold:.2f})."
            )

        return DuplicateCheckResult(
            is_duplicate=False,
            similarity_score=best_score,
            matched_feedback_id=None,
            matched_text=None,
            reason=f"No matching feedback met similarity threshold ({self.threshold:.2f}). Highest score: {best_score:.2f}."
        )
