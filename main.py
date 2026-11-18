"""HTTP endpoints for complaints and human review."""
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from graph import build_customer_care_graph
from schemas import ComplaintRequest, ComplaintResponse, HumanReviewRequest, HumanReviewResponse, PendingReviewResponse


app = FastAPI(title="Customer Care Agent")
workflow = build_customer_care_graph(checkpointer=InMemorySaver())
review_lock = Lock()


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/complaints", response_model=ComplaintResponse | PendingReviewResponse)
def submit_complaint(request: ComplaintRequest) -> ComplaintResponse | PendingReviewResponse:
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = workflow.invoke(request.model_dump(), config=config)

    if result.get("__interrupt__"):
        review = result["__interrupt__"][0].value
        return PendingReviewResponse(
            thread_id=thread_id,
            question=review["question"],
            complaint_text=review["complaint_text"],
        )

    return ComplaintResponse(
        category=result["category"],
        priority=result["priority"],
        ticket_ref=result.get("ticket_ref"),
        response=result["response"],
    )


@app.post("/api/v1/reviews/{thread_id}/resume", response_model=HumanReviewResponse)
def resume_review(thread_id: str, request: HumanReviewRequest) -> HumanReviewResponse:
    config = {"configurable": {"thread_id": thread_id}}

    # Check and resume together so two reviewers cannot complete the same local review.
    with review_lock:
        snapshot = workflow.get_state(config)
        if not any(task.interrupts for task in snapshot.tasks):
            raise HTTPException(status_code=404, detail="No pending review for this thread ID.")
        result = workflow.invoke(Command(resume=request.approved), config=config)

    return HumanReviewResponse(response=result["response"], ticket_ref=result.get("ticket_ref"))
