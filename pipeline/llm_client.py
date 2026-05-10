"""Shared LLM client with automatic provider failover.

Primary provider: Cerebras (fast inference, free tier)
Fallback provider: Together AI (larger daily quota, same model)

Set CEREBRAS_API_KEY and optionally TOGETHER_API_KEY in .env.
If Cerebras returns a rate-limit or queue error, call_llm() automatically
retries on Together AI. If Together AI is not configured, the error propagates
as normal.
"""

import os

# Provider-specific model names for the same underlying Qwen3-235B model
CEREBRAS_MODEL = "qwen-3-235b-a22b-instruct-2507"
TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Kept for backwards compatibility — callers that reference LLM_MODEL directly
# still work; call_llm() ignores any model kwarg and uses the provider's own name.
LLM_MODEL = CEREBRAS_MODEL


def get_llm_client():
    """Return the Cerebras client (kept for backwards compatibility)."""
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


def _get_together_client():
    """Return the Together AI client, or None if not configured."""
    if not hasattr(_get_together_client, "_client"):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            _get_together_client._client = None
        else:
            from openai import OpenAI
            _get_together_client._client = OpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1",
            )

    return _get_together_client._client


def _is_transient_provider_error(e: Exception) -> bool:
    """True for rate-limit or queue errors that may succeed on another provider."""
    msg = str(e).lower()
    # Don't fail over for daily token limits — those are account-level
    if "tokens per day" in msg or "tpd" in msg:
        return False
    return (
        "queue" in msg
        or "rate" in msg
        or "too many" in msg
        or "429" in str(getattr(e, "status_code", ""))
        or "503" in str(getattr(e, "status_code", ""))
    )


def call_llm(**kwargs) -> object:
    """Make an LLM completion call with automatic provider failover.

    Tries Cerebras first. If Cerebras returns a transient error (rate limit,
    queue overflow), immediately retries on Together AI if configured.

    Pass the same kwargs as openai client.chat.completions.create(), minus
    'model' — that is set per-provider automatically.

    Raises the last provider's exception if all providers fail.
    """
    kwargs.pop("model", None)  # provider model names are set here, not by callers

    # --- Try Cerebras ---
    cerebras_exc = None
    try:
        client = get_llm_client()
        return client.chat.completions.create(model=CEREBRAS_MODEL, **kwargs)
    except Exception as e:
        if not _is_transient_provider_error(e):
            raise  # daily limit, auth error, etc. — propagate immediately
        cerebras_exc = e
        print("  [Cerebras unavailable, switching to Together AI...]", flush=True)

    # --- Try Together AI ---
    together_client = _get_together_client()
    if together_client is None:
        raise cerebras_exc  # Together AI not configured — propagate original error

    return together_client.chat.completions.create(model=TOGETHER_MODEL, **kwargs)
