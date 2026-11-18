import os

from sqlalchemy import create_engine, text



database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://ccuser:ccpassword@127.0.0.1:5432/customer_care",
)
engine = create_engine(database_url, pool_pre_ping=True)


def check_database_connection() -> None:
    """Verify that Python can query the tickets table."""
    with engine.connect() as connection:
        ticket_count = connection.execute(
            text("SELECT COUNT(*) FROM tickets")
        ).scalar_one()

    print(f"Database connection successful. Tickets: {ticket_count}")


if __name__ == "__main__":
    check_database_connection()