"""Shared Groq LLM client — used by extract.py and rewrite.py."""

import os

LLM_MODEL = "llama-3.3-70b-versatile"


def get_llm_client():
    """Lazily create and cache the Groq client."""
    if not hasattr(get_llm_client, "_client"):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Add it to .env or set the env var."
            )

        from groq import Groq
        get_llm_client._client = Groq(api_key=api_key)

    return get_llm_client._client
