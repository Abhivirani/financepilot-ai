"""
Unit tests for the AI module.

These tests verify:
  - Context dataclass construction and immutability
  - AIService placeholder responses (with and without an LLM client)
  - LLM client factory routing
  - BaseLLMClient / GeminiClient / ClaudeClient interface contracts
  - InMemoryCache operations
"""

import pytest
from backend.app.ai.context_builder import (
    ExceptionContext,
    ChatContext,
    ReportSummaryContext,
)
from backend.app.ai.ai_service import AIService, ExplanationResult, ChatResult, ReportSummaryResult
from backend.app.ai.llm_client import (
    BaseLLMClient,
    GeminiClient,
    ClaudeClient,
    LLMResponse,
    create_llm_client,
)
from backend.app.core.cache import InMemoryCache


# ──────────────────────────────────────────────
# Context Builder dataclass tests
# ──────────────────────────────────────────────

class TestContextDataclasses:
    """Verify that context dataclasses are constructable and immutable."""

    def test_exception_context_required_fields(self):
        ctx = ExceptionContext(
            exception_id="exc-001",
            rule_type="AMOUNT_MISMATCH",
            severity="HIGH",
            transaction_id="txn-123",
            amount=100.50,
            currency="USD",
        )
        assert ctx.exception_id == "exc-001"
        assert ctx.bank_record is None  # optional, defaults to None

    def test_exception_context_is_frozen(self):
        ctx = ExceptionContext(
            exception_id="exc-001",
            rule_type="AMOUNT_MISMATCH",
            severity="HIGH",
            transaction_id="txn-123",
            amount=100.0,
            currency="USD",
        )
        with pytest.raises(AttributeError):
            ctx.exception_id = "changed"  # type: ignore

    def test_chat_context(self):
        ctx = ChatContext(
            user_message="Why was EX-001 flagged?",
            conversation_history=[{"role": "user", "content": "Hi"}],
        )
        assert ctx.run_id is None

    def test_report_summary_context(self):
        ctx = ReportSummaryContext(
            run_id="run-001",
            total_transactions=1000,
            matched_count=950,
            exception_count=50,
            financial_summary={"total": 50000.0},
            rule_distribution=[{"rule": "AMOUNT_MISMATCH", "count": 30}],
        )
        assert ctx.total_transactions == 1000


# ──────────────────────────────────────────────
# LLM Client tests
# ──────────────────────────────────────────────

class TestLLMClientFactory:
    """Verify that create_llm_client() returns the correct concrete type."""

    def test_factory_returns_gemini(self):
        client = create_llm_client(
            "gemini", api_key="test", model="gemini-2.5-flash",
            max_tokens=1024, temperature=0.3, timeout=30,
        )
        assert isinstance(client, GeminiClient)
        assert isinstance(client, BaseLLMClient)

    def test_factory_returns_claude(self):
        client = create_llm_client(
            "anthropic", api_key="test", model="claude-sonnet-4-20250514",
            max_tokens=1024, temperature=0.3, timeout=30,
        )
        assert isinstance(client, ClaudeClient)
        assert isinstance(client, BaseLLMClient)

    def test_factory_case_insensitive(self):
        client = create_llm_client(
            "  Gemini  ", api_key="test", model="m",
            max_tokens=1024, temperature=0.3, timeout=30,
        )
        assert isinstance(client, GeminiClient)

    def test_factory_rejects_unknown_provider(self):
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            create_llm_client(
                "openai", api_key="test", model="gpt-4",
                max_tokens=1024, temperature=0.3, timeout=30,
            )





class TestClaudeClientPlaceholder:
    """ClaudeClient.generate() should raise NotImplementedError."""

    @pytest.mark.asyncio
    async def test_generate_not_implemented(self):
        client = ClaudeClient(
            api_key="test", model="claude-sonnet-4-20250514",
            default_max_tokens=1024, default_temperature=0.3, timeout=30,
        )
        with pytest.raises(NotImplementedError, match="ClaudeClient"):
            await client.generate(system="sys", messages=[{"role": "user", "content": "hi"}])


# ──────────────────────────────────────────────
# AI Service placeholder tests
# ──────────────────────────────────────────────

class TestAIServicePlaceholders:
    """Verify that every AIService method returns a deterministic placeholder."""

    @pytest.fixture
    def service(self):
        return AIService()

    def test_service_not_active_without_client(self, service):
        assert service.is_active is False

    def test_service_active_with_client(self):
        client = GeminiClient(
            api_key="x", model="m",
            default_max_tokens=1024, default_temperature=0.3, timeout=30,
        )
        service = AIService(llm_client=client)
        assert service.is_active is True

    @pytest.mark.asyncio
    async def test_explain_exception_returns_placeholder(self, service):
        result = await service.explain_exception("exc-123")
        assert isinstance(result, ExplanationResult)
        assert "exc-123" in result.explanation
        assert result.source == "placeholder"
        assert result.confidence == "low"
        assert len(result.suggested_actions) > 0

    @pytest.mark.asyncio
    async def test_chat_returns_placeholder(self, service):
        result = await service.chat("What happened?")
        assert isinstance(result, ChatResult)
        assert result.source == "placeholder"
        assert len(result.suggested_questions) > 0

    @pytest.mark.asyncio
    async def test_summarize_report_returns_placeholder(self, service):
        result = await service.summarize_report("run-001")
        assert isinstance(result, ReportSummaryResult)
        assert "run-001" in result.summary
        assert result.source == "placeholder"


# ──────────────────────────────────────────────
# Cache tests
# ──────────────────────────────────────────────

class TestInMemoryCache:
    """Verify the InMemoryCache interface contract."""

    @pytest.fixture
    def cache(self):
        return InMemoryCache()

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_get_miss(self, cache):
        assert await cache.get("nonexistent") is None

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        await cache.set("key1", "value1")
        await cache.delete("key1")
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_invalidate_prefix(self, cache):
        await cache.set("ai:exc:001", "v1")
        await cache.set("ai:exc:002", "v2")
        await cache.set("ai:chat:001", "v3")
        deleted = await cache.invalidate_prefix("ai:exc:")
        assert deleted == 2
        assert await cache.get("ai:chat:001") == "v3"

    @pytest.mark.asyncio
    async def test_clear(self, cache):
        await cache.set("a", 1)
        await cache.set("b", 2)
        await cache.clear()
        assert await cache.get("a") is None
        assert await cache.get("b") is None
