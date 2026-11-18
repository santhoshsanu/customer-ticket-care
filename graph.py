"""Route complaints to a published resolution, ticket creation, or human review."""
from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from nodes import classify_complaint, decide_next_action
from sql_agent_service import find_known_resolution
from state import CustomerCareState, NextAction
from ticket_repository import create_ticket


def lookup_resolution(state: CustomerCareState) -> CustomerCareState:
    if state["priority"] == "critical":
        return {"known_resolution_found": False, "known_resolution": None}
    resolution = find_known_resolution(state["complaint_text"], state.get("product_hint"))
    return {"known_resolution_found": resolution is not None, "known_resolution": resolution}


def route_after_decision(state: CustomerCareState) -> NextAction:
    return state["next_action"]


def known_resolution_response(state: CustomerCareState) -> CustomerCareState:
    return {"response": state["known_resolution"]}


def create_ticket_node(state: CustomerCareState) -> CustomerCareState:
    ticket_id = create_ticket(
        complaint_text=state["complaint_text"],
        product_hint=state.get("product_hint"),
        category=state["category"],
        priority=state["priority"],
    )
    ticket_ref = f"TKT-{ticket_id}"
    return {"ticket_ref": ticket_ref, "response": f"Support ticket {ticket_ref} was created."}


def human_review_preview(state: CustomerCareState) -> CustomerCareState:
    return {"response": "This complaint needs human review."}


def pause_for_human_review(
    state: CustomerCareState,
) -> Command[Literal["create_ticket", "__end__"]]:
    decision = interrupt({
        "question": "Should this grievance be escalated?",
        "complaint_text": state["complaint_text"],
    })
    if decision is True:
        return Command(goto="create_ticket")
    return Command(update={"response": "Reviewer declined escalation."}, goto=END)


def build_customer_care_graph(checkpointer: InMemorySaver | None = None):
    builder = StateGraph(CustomerCareState)
    builder.add_node("classify_complaint", classify_complaint)
    builder.add_node("lookup_resolution", lookup_resolution)
    builder.add_node("decide_next_action", decide_next_action)
    builder.add_node("known_resolution", known_resolution_response)
    builder.add_node("create_ticket", create_ticket_node)

    if checkpointer is None:
        builder.add_node("human_review", human_review_preview)
        builder.add_edge("human_review", END)
    else:
        builder.add_node("human_review", pause_for_human_review)

    builder.add_edge(START, "classify_complaint")
    builder.add_edge("classify_complaint", "lookup_resolution")
    builder.add_edge("lookup_resolution", "decide_next_action")
    builder.add_conditional_edges(
        "decide_next_action",
        route_after_decision,
        {
            "known_resolution": "known_resolution",
            "create_ticket": "create_ticket",
            "human_review": "human_review",
        },
    )
    builder.add_edge("known_resolution", END)
    builder.add_edge("create_ticket", END)
    return builder.compile(checkpointer=checkpointer)


customer_care_graph = build_customer_care_graph()
