from typing import Literal, TypedDict


Category = Literal[
    "product_defect",
    "warranty_claim",
    "installation_support",
    "software_issue",
    "shipping_damage",
    "returns_refunds",
    "billing",
    "general_inquiry",
]

Priority = Literal["low", "medium", "high", "critical"]

NextAction = Literal[
    "known_resolution",
    "create_ticket",
    "human_review",
]


class CustomerCareState(TypedDict, total=False):
    """Information carried through the workflow for one complaint."""

    # Input from the customer
    complaint_text: str
    product_hint: str | None

    # Information added during processing
    category: Category
    priority: Priority
    known_resolution_found: bool
    known_resolution: str | None
    next_action: NextAction

    # Information added when the workflow finishes
    ticket_ref: str | None
    response: str | None
