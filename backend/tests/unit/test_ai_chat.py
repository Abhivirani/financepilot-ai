import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from backend.app.ai.context_builder import ChatContext, DashboardSummaryContext
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.ai.ai_service import AIService
from backend.app.ai.llm_client import BaseLLMClient, LLMResponse

@pytest.fixture
def mock_dashboard_context():
    return DashboardSummaryContext(
        run_id="run_123",
        total_transactions=1000,
        matched_transactions=900,
        unmatched_transactions=100,
        total_exceptions=100,
        match_rate=90.0,
        critical_exceptions=10,
        financial_summary={"total_gateway_volume": 100000, "total_settled_volume": 90000},
        rule_distribution=[{"rule_type": "MISSING", "count": 100}],
        source_volume=[{"source_type": "BANK", "count": 1000}]
    )

@pytest.fixture
def mock_chat_context(mock_dashboard_context):
    return ChatContext(
        user_message="Why is the match rate low?",
        conversation_history=[],
        run_id="run_123",
        dashboard_context=mock_dashboard_context
    )

def test_chat_system_prompt_interpolation(mock_chat_context):
    builder = PromptBuilder()
    prompt = builder.get_system_prompt(mock_chat_context)
    
    assert "90.0%" in prompt
    assert "100" in prompt
    assert "MISSING" in prompt
    assert "FinancePilot AI" in prompt

@pytest.mark.asyncio
async def test_ai_service_chat():
    mock_llm = AsyncMock(spec=BaseLLMClient)
    mock_llm.generate.return_value = LLMResponse(
        content="The match rate is low due to MISSING rules.\n\nConfidence: 94%",
        model="gemini-mock",
        usage={"total": 100}
    )
    
    mock_context_builder = AsyncMock()
    mock_context_builder.build_chat_context.return_value = ChatContext(
        user_message="Test",
        conversation_history=[]
    )
    
    mock_prompt_builder = MagicMock()
    mock_prompt_builder.build_chat_messages.return_value = [{"role": "user", "content": "Test"}]
    mock_prompt_builder.get_system_prompt.return_value = "System"
    
    service = AIService(
        llm_client=mock_llm,
        context_builder=mock_context_builder,
        prompt_builder=mock_prompt_builder
    )
    
    result = await service.chat("Test")
    
    assert result.confidence == 94
    assert "MISSING rules" in result.answer
    assert "Confidence:" not in result.answer  # Should be stripped
    assert result.source == "llm"
