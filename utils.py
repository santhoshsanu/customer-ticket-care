"""Create the configured chat model for the knowledge agent."""
import os
from functools import lru_cache


def model_provider() -> str:
    return os.getenv("MODEL_PROVIDER", "local").strip().lower()


@lru_cache(maxsize=1)
def get_llm():
    provider = model_provider()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-5.4-mini"), max_retries=2)

    if provider == "bedrock":
        from langchain_aws import ChatBedrockConverse

        return ChatBedrockConverse(
            model_id=os.environ["MODEL_NAME"],
            region_name=os.environ["AWS_REGION"],
            credentials_profile_name=os.getenv("AWS_PROFILE"),
        )

    raise ValueError(f"No chat model configured for MODEL_PROVIDER={provider!r}")
