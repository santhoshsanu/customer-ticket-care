from sqlalchemy import text

from database import engine
from state import Category, Priority



def create_ticket(
    *,
    complaint_text: str,
    category: Category,
    priority: Priority,
    product_hint: str | None = None,
) -> int:
    """Save a complaint as a ticket and return its database ID."""
    statement = text("""
        INSERT INTO tickets (complaint_text, product_hint, category, priority)
        VALUES (:complaint_text, :product_hint, :category, :priority)
        RETURNING id
    """)

    with engine.begin() as connection:
        ticket_id = connection.execute(
            statement,
            {
                "complaint_text": complaint_text,
                "product_hint": product_hint,
                "category": category,
                "priority": priority,
            },
        ).scalar_one()

    return ticket_id