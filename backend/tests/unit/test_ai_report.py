import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.app.ai.context_builder import ReportSummaryContext
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.ai.ai_service import AIService
from backend.app.ai.llm_client import BaseLLMClient, LLMResponse

@pytest.fixture
def mock_report_context():
    return ReportSummaryContext(
        run_id="run_123",
        total_transactions=12320,
        matched_transactions=11740,
        unmatched_transactions=580,
        total_exceptions=580,
        match_rate=95.2,
        critical_exceptions=12,
        financial_summary={"total_gateway_volume": 54321000, "total_settled_volume": 53812000},
        rule_distribution=[{"rule_type": "MISSING_SETTLEMENT", "count": 200}],
        source_volume=[{"source_type": "GATEWAY", "count": 12320}]
    )

def test_executive_report_prompt_interpolation(mock_report_context):
    builder = PromptBuilder()
    messages = builder.build_report_messages(mock_report_context)
    prompt = messages[0]["content"]
    
    assert "12320" in prompt
    assert "95.2%" in prompt
    assert "MISSING_SETTLEMENT" in prompt
    assert "Executive Summary" in prompt

@pytest.mark.asyncio
async def test_ai_service_generate_executive_report():
    mock_llm = AsyncMock(spec=BaseLLMClient)
    mock_llm.generate.return_value = LLMResponse(
        content="# Executive Summary\nTest Summary\n\n# Overall Health\nGood.\n\nConfidence: 96%",
        model="gemini-mock",
        input_tokens=100,
        output_tokens=50,
        stop_reason="stop"
    )
    
    mock_context_builder = AsyncMock()
    mock_context_builder.build_report_summary_context.return_value = ReportSummaryContext(
        run_id="run_123", total_transactions=0, matched_transactions=0, unmatched_transactions=0, total_exceptions=0,
        match_rate=0, critical_exceptions=0, financial_summary={}, rule_distribution=[], source_volume=[]
    )
    
    mock_prompt_builder = MagicMock()
    mock_prompt_builder.build_report_messages.return_value = [{"role": "user", "content": "Test"}]
    
    service = AIService(
        llm_client=mock_llm,
        context_builder=mock_context_builder,
        prompt_builder=mock_prompt_builder
    )
    
    result = await service.generate_executive_report()
    
    assert result.confidence == 96
    assert result.summary == "Test Summary"
    assert "# Overall Health" in result.markdown
    assert result.source == "llm"
