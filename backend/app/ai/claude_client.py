# ──────────────────────────────────────────────────────────────────────
# DEPRECATED — this file has been superseded by llm_client.py
#
# All LLM logic now lives in llm_client.py which provides:
#   - BaseLLMClient   (abstract interface)
#   - GeminiClient    (primary provider)
#   - ClaudeClient    (future provider)
#   - create_llm_client()  (factory)
#
# This file is kept only so that existing imports do not break.
# Do NOT add new code here.  Import from llm_client instead.
# ──────────────────────────────────────────────────────────────────────

from backend.app.ai.llm_client import (  # noqa: F401 — re-exports for back-compat
    LLMResponse,
    BaseLLMClient,
    ClaudeClient,
    GeminiClient,
    create_llm_client,
)
