# Customer Care Agent

Run this Python 3.13 project from PowerShell with Docker Desktop running.

## Start the local workflow

    uv sync
    docker compose up -d --wait
    Get-Content -Raw .\customercaredb\init.sql | docker compose exec -T postgres psql -U ccuser -d customer_care -v ON_ERROR_STOP=1 -f -
    if (-not (Test-Path .env)) { Copy-Item .env.example .env }
    uv run --env-file .env python database.py
    uv run --env-file .env fastapi dev main.py

The SQL command also updates an existing Docker volume. It is safe to reapply and preserves existing tickets. The mounted script initializes fresh volumes automatically.

Open the Swagger UI at http://127.0.0.1:8000/docs and send sample complaints to POST /api/v1/complaints.

| Complaint text | Expected result |
| --- | --- |
| My headphones are not pairing. | A published Bluetooth fix and a null ticket reference |
| My tablet arrived damaged during delivery. | A ticket reference such as TKT-5 |
| My tablet arrived cracked. I will go to consumer court. | A review question and a thread ID |

For a review, send {"approved": true} or {"approved": false} to POST /api/v1/reviews/{thread_id}/resume. Approval creates a critical ticket. Decline ends the review. Checkpoints are kept in memory and disappear when FastAPI restarts or reloads. Run a single server process for this local demo.

## Optional live LLM

The default MODEL_PROVIDER=local uses phrase matching against the published resolution table. Edit your local .env and run one of these commands.

    # OpenAI
    uv run --extra openai --env-file .env fastapi dev main.py

    # Amazon Bedrock
    uv run --extra bedrock --env-file .env fastapi dev main.py

For OpenAI, set MODEL_PROVIDER=openai, MODEL_NAME=gpt-5.4-mini, and OPENAI_API_KEY. For Bedrock, set MODEL_PROVIDER=bedrock, MODEL_NAME to a Converse-compatible model or inference profile with tool support, AWS_REGION to its source region, and AWS_PROFILE if you use a named profile. For an SSO profile, sign in through the AWS CLI before starting the app. The AWS identity needs permission to invoke the chosen model.

Nova 2 Lite example: set MODEL_NAME=us.amazon.nova-2-lite-v1:0 and AWS_REGION=us-east-1. Leave AWS_PROFILE out when your default AWS CLI credentials already work. Test the model with:

    uv run --locked --extra bedrock --env-file .env python -c "from utils import get_llm; print(get_llm().invoke('Reply with OK').content)"

The model can call the published-resolution search tool. The tool executes a fixed parameterized SELECT. Ticket creation is handled by the Python repository. Use sample complaints in this local demo.

## Run tests

    uv run python -m unittest discover -s tests -v

The workflow tests use the FastAPI test client and replace database and provider calls. Use the Swagger checks above for the live PostgreSQL workflow. Stop the containers with docker compose stop when finished.
