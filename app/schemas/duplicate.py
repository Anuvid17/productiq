from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DuplicateCheckResult(BaseModel):
    """
    Structured response representing the duplicate analysis result.
    Does NOT fabricate feedback IDs or alter taxonomy names.
    """
    is_duplicate: bool = Field(..., description="True if new feedback matches existing record above threshold")
    similarity_score: float = Field(..., description="Cosine similarity score between 0.0 and 1.0")
    matched_feedback_id: Optional[str] = Field(default=None, description="UUID of matched existing feedback record if duplicate")
    matched_text: Optional[str] = Field(default=None, description="Original text of matched existing feedback")
    reason: str = Field(..., description="Human-readable explanation of duplicate decision")

    model_config = ConfigDict(from_attributes=True)
