# AI Module — `backend/app/ai/`

## Purpose

This package contains all AI/LLM-related logic for FinancePilot.
It is structured as a clean, **provider-agnostic** pipeline:

```
Request  →  ContextBuilder  →  PromptBuilder  →  BaseLLMClient.generate()  →  Response
                 ↑                                        ↑
            StateStore                          GeminiClient / ClaudeClient
```

## Files

| File | Responsibility |
|---|---|
| `context_builder.py` | Gathers domain data (exceptions, transactions, reports) into immutable context dataclasses. |
| `prompt_builder.py` | Loads Markdown templates from `prompts/` and renders them with context data. |
| `llm_client.py` | `BaseLLMClient` interface, `GeminiClient`, `ClaudeClient`, and `create_llm_client()` factory. |
| `ai_service.py` | Orchestration facade. Depends on `BaseLLMClient` — **never** imports a concrete provider. |
| `claude_client.py` | **Deprecated** — re-exports from `llm_client.py` for backward compatibility. |
| `llm.py` | **Deprecated** — legacy stub. |

## Prompt Templates

All prompts live in `prompts/` as Markdown files:

- `exception_explanation.md` — Exception analysis prompt
- `report_summary.md` — Report summarisation prompt
- `chat_system.md` — System prompt for conversational chat

**Never hardcode prompts in Python files.**

## Configuration

All LLM settings are centralised in `backend/app/core/config.py`:

- `LLM_PROVIDER` — Provider identifier: `"gemini"` or `"anthropic"` (default: `"gemini"`)
- `LLM_MODEL` — Model name (default: `"gemini-2.5-flash"`)
- `LLM_TEMPERATURE` — Sampling temperature (default: `0.3`)
- `LLM_MAX_TOKENS` — Maximum output tokens (default: `2048`)
- `LLM_TIMEOUT` — Request timeout in seconds (default: `30`)
- `LLM_CACHE_TTL` — Cache TTL in seconds (default: `3600`)
- `GEMINI_API_KEY` — Google Gemini API key (from `.env`)
- `ANTHROPIC_API_KEY` — Anthropic API key (from `.env`, future)

## Adding a New Provider

1. Create a new class in `llm_client.py` implementing `BaseLLMClient`.
2. Add a branch in `create_llm_client()`.
3. Add the API key field to `Settings`.
4. Set `LLM_PROVIDER` in `.env`.

No other file needs to change.

## Status

🟡 **Interfaces only** — no LLM calls are made yet. Every public method
in `ai_service.py` returns a deterministic placeholder response.
