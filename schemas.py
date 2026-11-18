from typing import Literal

from pydantic import BaseModel, Field, StrictBool

from state import Category, Priority


class ComplaintRequest(BaseModel):
    """Data submitted by the customer."""

    complaint_text: str = Field(min_length=1)
    product_hint: str | None = None


class ComplaintResponse(BaseModel):
    """Classification and optional ticket reference returned to the caller."""

    category: Category
    priority: Priority
    ticket_ref: str | None = None
    response: str | None = None


class PendingReviewResponse(BaseModel):
    """Details returned when a grievance pauses for human review."""

    status: Literal["human_review_required"] = "human_review_required"
    thread_id: str
    question: str
    complaint_text: str


class HumanReviewRequest(BaseModel):
    """Decision submitted by the reviewer."""

    approved: StrictBool


class HumanReviewResponse(BaseModel):
    """Outcome of a completed human review."""

    response: str
    status: Literal["resumed"] = "resumed"
    ticket_ref: str | None = None
