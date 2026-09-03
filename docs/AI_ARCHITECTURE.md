# AI Architecture — FinancePilot

## Overview

FinancePilot AI adds LLM-powered intelligence to the existing reconciliation
platform. Users can ask the AI to explain exceptions, summarise reports, and
suggest resolution strategies — all grounded in their actual data.

The architecture is designed around three principles:

1. **Separation of concerns** — data gathering, prompt rendering, and LLM
   calling live in distinct, independently testable modules.
2. **Provider agnosticism** — the `BaseLLMClient` interface means any provider
   (Gemini, Claude, OpenAI, local models) can be swapped with a single config
   change. `ai_service.py` **never** imports a concrete client.
3. **Graceful degradation** — every AI feature works in placeholder mode when
   no API key is configured.

---

## Architecture Diagram

```mermaid
flowchart LR
    subgraph Frontend
        A[AI Page / Chat] -->|useAIExplain / useAIChat| B[API Service Layer]
    end

    subgraph "FastAPI - API Layer"
        B --> C[POST /ai/explain]
        B --> D[POST /ai/chat]
        B --> E[POST /ai/summarize]
    end

    subgraph "AI Module - backend/app/ai/"
        C --> F[AIService]
        D --> F
        E --> F
        F --> G[ContextBuilder]
        F --> H[PromptBuilder]
        F -->|".generate()"| I["BaseLLMClient"]
        F --> J[Cache]
    end

    subgraph "LLM Providers - llm_client.py"
        I --> I1[GeminiClient]
        I --> I2["ClaudeClient (future)"]
    end

    subgraph "Data Layer"
        G --> K[StateStore]
        G --> L[Reconciliation Engine]
    end

    subgraph "External APIs"
        I1 --> M1[Google Gemini API]
        I2 --> M2[Anthropic Messages API]
    end

    subgraph "Templates"
        H --> N["prompts/exception_explanation.md"]
        H --> O["prompts/report_summary.md"]
        H --> P["prompts/chat_system.md"]
    end
```

---

## Component Details

### 1. Context Builder (`context_builder.py`)

**Purpose:** Gather all domain data the LLM needs to produce a grounded answer.

| Input | Output |
|---|---|
| Exception ID | `ExceptionContext` — exception details, bank record, gateway record |
| Chat message | `ChatContext` — message, history, active run metadata |
| Run ID | `ReportSummaryContext` — financial summary, rule distribution |

**Key decisions:**
- Context objects are frozen dataclasses — immutable snapshots.
- The builder queries `StateStore` but never mutates it.
- A future token budget parameter will truncate context to stay within
  the model's window.

### 2. Prompt Builder (`prompt_builder.py`)

**Purpose:** Render domain context into the `messages` list expected by
`BaseLLMClient.generate()`.

- Templates live in `prompts/` as Markdown files — **never hardcoded**.
- Uses Python `string.Template` for `$variable` interpolation.
- The system prompt is loaded from `chat_system.md` and passed separately.

### 3. LLM Client (`llm_client.py`)

**Purpose:** Provider-agnostic adapter layer.

| Class | Provider | Status |
|---|---|---|
| `BaseLLMClient` | Abstract interface | ✅ Defined |
| `GeminiClient` | Google Gemini | 🟡 Stub |
| `ClaudeClient` | Anthropic Claude | 🟡 Stub |
| `create_llm_client()` | Factory function | ✅ Implemented |

**Key rule:** `ai_service.py` never imports `GeminiClient` or `ClaudeClient`.
It calls `create_llm_client()` or receives a `BaseLLMClient` via DI.

### 4. AI Service (`ai_service.py`)

**Purpose:** Orchestration facade called by the FastAPI endpoint layer.

```
explain_exception(id) → ContextBuilder → PromptBuilder → client.generate() → Response
chat(message)         → ContextBuilder → PromptBuilder → client.generate() → Response
summarize_report(id)  → ContextBuilder → PromptBuilder → client.generate() → Response
```

Each method checks the cache first and stores responses after a successful
LLM call.

---

## LLM Flow (Request Lifecycle)

```
1. HTTP request hits /ai/explain
2. FastAPI validates the Pydantic schema
3. AIService.explain_exception() is called
4. ContextBuilder fetches the exception + related records from StateStore
5. PromptBuilder renders exception_explanation.md with the context
6. Cache is checked — if hit, return immediately
7. self._llm.generate(system=..., messages=...) calls the active provider
8. Response is cached with configurable TTL
9. Structured result is returned to the frontend
```

---

## Token Optimisation Strategy

| Strategy | Status |
|---|---|
| Context truncation to stay within window | 🟡 Planned |
| Prompt template minification (remove comments before sending) | 🟡 Planned |
| Response caching by (exception_id + data hash) | 🟡 Interface ready |
| Streaming responses for long explanations | 🔴 Future |
| Batch explanation for multiple exceptions | 🔴 Future |

**Token budget allocation (per request):**
- System prompt: ~500 tokens
- User context: ~1,500 tokens (max)
- Model response: up to `LLM_MAX_TOKENS` (default 2,048)

---

## Configuration

All LLM settings live in `backend/app/core/config.py`:

```python
LLM_PROVIDER: str = "gemini"              # "gemini" | "anthropic"
LLM_MODEL: str = "gemini-2.5-flash"
LLM_TEMPERATURE: float = 0.3
LLM_MAX_TOKENS: int = 2048
LLM_TIMEOUT: int = 30                     # seconds
LLM_CACHE_TTL: int = 3600                 # seconds
GEMINI_API_KEY: str = ""                   # from .env
ANTHROPIC_API_KEY: str = ""                # from .env (future)
```

---

## Adding a New Provider

1. Create a new class in `llm_client.py` implementing `BaseLLMClient.generate()`.
2. Add a branch in `create_llm_client()`.
3. Add the API key field to `Settings` in `config.py`.
4. Set `LLM_PROVIDER=your_provider` in `.env`.

No other file needs to change.

---

## Future: MCP (Model Context Protocol) Support

FinancePilot's architecture is pre-aligned for MCP adoption:

| MCP Concept | FinancePilot Equivalent |
|---|---|
| **Tools** | `ContextBuilder` methods become tool functions the model can invoke |
| **Resources** | `StateStore` data (exceptions, reports) exposed as typed resources |
| **Prompts** | `prompts/` directory already externalises prompt templates |

When MCP support is added:
1. Each `ContextBuilder` method is registered as an MCP tool.
2. The model decides which tools to call based on the user's question.
3. Tool results are automatically injected into the conversation context.

This will allow the AI to dynamically pull exactly the data it needs
rather than receiving a pre-built context blob.

---

## File Map

```
backend/app/ai/
├── __init__.py
├── README.md
├── ai_service.py          ← Orchestration facade (depends on BaseLLMClient only)
├── llm_client.py          ← BaseLLMClient, GeminiClient, ClaudeClient, factory
├── claude_client.py       ← DEPRECATED re-export shim
├── context_builder.py     ← Domain data gathering
├── prompt_builder.py      ← Template rendering
├── llm.py                 ← DEPRECATED legacy stub
└── prompts/
    ├── chat_system.md
    ├── exception_explanation.md
    └── report_summary.md

backend/app/core/
├── cache.py               ← Cache interface + InMemoryCache
└── config.py              ← LLM_* settings

frontend/src/components/ai/
├── ChatWindow.tsx
├── ConfidenceBadge.tsx
├── MessageBubble.tsx
├── SuggestionChip.tsx
├── ThinkingIndicator.tsx
└── index.ts

frontend/src/types/
└── ai.ts                  ← Shared AI type definitions

frontend/src/lib/api/services/
└── ai.ts                  ← explainException, chat, summarizeReport
```
