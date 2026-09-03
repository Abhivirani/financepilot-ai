from fastapi import APIRouter
from backend.app.schemas.ai import AIExplainRequest, AIExplainResponseData, AIDashboardSummaryResponseData, AIChatRequest, AIChatResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.ai.ai_service import AIService
from backend.app.ai.llm_client import create_llm_client
from backend.app.core.config import settings
from backend.app.ai.context_builder import DefaultContextBuilder
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.services.state_store import state_store

router = APIRouter()

# Instantiate AI Service dependencies
try:
    llm_client = create_llm_client(
        provider=settings.LLM_PROVIDER,
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE,
        timeout=settings.TIMEOUT
    )
except Exception:
    llm_client = None

context_builder = DefaultContextBuilder(state_store=state_store)
prompt_builder = PromptBuilder()
ai_service = AIService(
    llm_client=llm_client, 
    context_builder=context_builder, 
    prompt_builder=prompt_builder
)

@router.post("/ai/explain", response_model=SuccessResponse[AIExplainResponseData])
async def explain_exception(req: AIExplainRequest):
    result = await ai_service.explain_exception(req.exception_id)
    return SuccessResponse(
        data=AIExplainResponseData(
            summary=result.summary,
            markdown=result.markdown,
            confidence=result.confidence,
            latency_ms=result.latency_ms
        )
    )

@router.post("/ai/dashboard-summary", response_model=SuccessResponse[AIDashboardSummaryResponseData])
async def dashboard_summary():
    from datetime import datetime
    result = await ai_service.generate_dashboard_summary()
    return SuccessResponse(
        data=AIDashboardSummaryResponseData(
            summary=result.summary,
            markdown=result.markdown,
            confidence=result.confidence,
            latency_ms=result.latency_ms,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
    )

@router.post("/ai/chat", response_model=SuccessResponse[AIChatResponseData])
async def chat(req: AIChatRequest):
    from datetime import datetime
    result = await ai_service.chat(req.message)
    return SuccessResponse(
        data=AIChatResponseData(
            answer=result.answer,
            confidence=result.confidence,
            latency_ms=result.latency_ms,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
    )
