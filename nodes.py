from state import Category, CustomerCareState, Priority


def classify_complaint(state: CustomerCareState) -> CustomerCareState:
    """Return a category and priority for the complaint."""
    complaint = state["complaint_text"].lower()

    shipping_damage_phrases = (
        "arrived cracked",
        "arrived damaged",
        "damaged in transit",
    )
    grievance_phrases = (
        "consumer court",
        "legal action",
    )

    category: Category = "general_inquiry"
    priority: Priority = "low"

    if any(phrase in complaint for phrase in shipping_damage_phrases):
        category = "shipping_damage"
        priority = "high"

    if any(phrase in complaint for phrase in grievance_phrases):
        priority = "critical"

    return {"category": category, "priority": priority}


def decide_next_action(state: CustomerCareState) -> CustomerCareState:
    """Choose the next step for a classified complaint."""
    if state.get("priority") == "critical":
        return {"next_action": "human_review"}

    if state.get("known_resolution_found", False):
        return {"next_action": "known_resolution"}

    return {"next_action": "create_ticket"}