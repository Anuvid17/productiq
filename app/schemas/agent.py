from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FeedbackAnalysis(BaseModel):
    """
    Pydantic schema representing the structured classification output
    from the FeedbackAgent after analyzing customer feedback.
    """
    summary: str = Field(..., description="Brief one-line summary of the user feedback")
    feedback_type: str = Field(..., description="Taxonomy Feedback Type (e.g. Bug Report, Feature Request)")
    category: str = Field(..., description="Top-level Taxonomy Category (e.g. Authentication, Billing & Subscription)")
    subcategory: str = Field(..., description="Taxonomy Subcategory belonging strictly to category")
    bug_category: Optional[str] = Field(default="N/A", description="Bug category if feedback_type is Bug Report")
    severity: str = Field(..., description="Severity level: Blocker, Critical, Major, Minor, Trivial")
    priority: str = Field(..., description="Priority level: P0, P1, P2, P3")
    impact_area: str = Field(..., description="Impact area: All Users, Enterprise Customers, Admin Users, etc.")
    platform: str = Field(default="Web", description="Platform: Web, Android, iOS, Desktop, API")
    recommended_action: str = Field(..., description="Agent Action: CREATE_BUG, CREATE_FEATURE, ESCALATE, etc.")
    confidence: str = Field(..., description="Confidence band: High, Medium, Low")

    # Optional analysis details
    reasoning: Optional[str] = Field(default=None, description="Step-by-step reasoning for taxonomy choices")
    missing_information: Optional[str] = Field(default=None, description="Details missing from user feedback if any")
    needs_more_information: Optional[bool] = Field(default=False, description="Flag indicating if customer follow-up is needed")

    model_config = ConfigDict(from_attributes=True)
