"""Shared Cerebras LLM client - used by extract.py and rewrite.py."""

import os

LLM_MODEL = "qwen-3-235b-a22b-instruct-2507"


def get_llm_client():
    """Lazily create and cache the Cerebras client."""
    if not hasattr(get_llm_client, "_client"):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("CEREBRAS_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CEREBRAS_API_KEY not set. Add it to .env or set the env var."
            )

        from openai import OpenAI
        get_llm_client._client = OpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1",
        )

    return get_llm_client._client
