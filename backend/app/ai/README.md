# AI Module — `backend/app/ai/`

## Purpose

This package contains all AI/LLM-related logic for FinancePilot.
It is structured as a clean pipeline with four distinct layers:

```
Request  →  ContextBuilder  →  PromptBuilder  →  ClaudeClient  →  Response
                 ↑                                     ↑
            StateStore                            Anthropic SDK
```

## Files

| File | Responsibility |
|---|---|
| `context_builder.py` | Gathers domain data (exceptions, transactions, reports) into immutable context dataclasses. |
| `prompt_builder.py` | Loads Markdown templates from `prompts/` and renders them with context data. |
| `claude_client.py` | Thin adapter over the Anthropic SDK. The **only** file that imports `anthropic`. |
| `ai_service.py` | Orchestration facade consumed by the API layer. Coordinates context → prompt → LLM → cache. |

## Prompt Templates

All prompts live in `prompts/` as Markdown files:

- `exception_explanation.md` — Exception analysis prompt
- `report_summary.md` — Report summarisation prompt
- `chat_system.md` — System prompt for conversational chat

**Never hardcode prompts in Python files.**

## Configuration

All AI settings are centralised in `backend/app/core/config.py`:

- `AI_PROVIDER` — LLM provider identifier (default: `"anthropic"`)
- `AI_MODEL` — Model name (default: `"claude-sonnet-4-20250514"`)
- `AI_TEMPERATURE` — Sampling temperature
- `AI_MAX_TOKENS` — Maximum output tokens
- `AI_TIMEOUT` — Request timeout in seconds
- `ANTHROPIC_API_KEY` — API key (from `.env`)

## Status

🟡 **Interfaces only** — no Claude calls are made yet. Every public method
in `ai_service.py` returns a deterministic placeholder response.
