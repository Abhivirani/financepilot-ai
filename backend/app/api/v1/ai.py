from fastapi import APIRouter
from backend.app.core.exceptions import APIException
from backend.app.ai.exceptions import AIError, LLMQuotaExceededError
from fastapi import HTTPException, status

from backend.app.schemas.ai import AIExplainRequest, AIExplainResponseData, AIDashboardSummaryResponseData, AIChatRequest, AIChatResponseData, AIExecutiveReportResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.ai.ai_service import AIService
from backend.app.ai.llm_client import create_llm_client
from backend.app.core.config import settings
from backend.app.ai.context_builder import DefaultContextBuilder
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.services.state_store import state_store

router = APIRouter()

# Instantiate AI Service dependencies
llm_client = create_llm_client(
    provider=settings.LLM_PROVIDER,
    api_key=settings.GEMINI_API_KEY,
    model=settings.GEMINI_MODEL,
    max_tokens=settings.MAX_TOKENS,
    temperature=settings.TEMPERATURE,
    timeout=settings.TIMEOUT
)

context_builder = DefaultContextBuilder(state_store=state_store)
prompt_builder = PromptBuilder()
ai_service = AIService(
    llm_client=llm_client, 
    context_builder=context_builder, 
    prompt_builder=prompt_builder
)

@router.post("/ai/explain", response_model=SuccessResponse[AIExplainResponseData])
async def explain_exception(req: AIExplainRequest):
    try:
        result = await ai_service.explain_exception(req.exception_id)
        return SuccessResponse(
            data=AIExplainResponseData(
                summary=result.summary,
                markdown=result.markdown,
                confidence=result.confidence,
                latency_ms=result.latency_ms
            )
        )
    except LLMQuotaExceededError as e:
        raise APIException(code='AI_QUOTA_EXCEEDED', http_status=status.HTTP_429_TOO_MANY_REQUESTS, message=str(e))
    except AIError as e:
        raise APIException(code='AI_SERVICE_ERROR', http_status=status.HTTP_503_SERVICE_UNAVAILABLE, message=str(e))

@router.post("/ai/dashboard-summary", response_model=SuccessResponse[AIDashboardSummaryResponseData])
async def dashboard_summary():
    try:
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
    except LLMQuotaExceededError as e:
        raise APIException(code='AI_QUOTA_EXCEEDED', http_status=status.HTTP_429_TOO_MANY_REQUESTS, message=str(e))
    except AIError as e:
        raise APIException(code='AI_SERVICE_ERROR', http_status=status.HTTP_503_SERVICE_UNAVAILABLE, message=str(e))

@router.post("/ai/chat", response_model=SuccessResponse[AIChatResponseData])
async def chat(req: AIChatRequest):
    try:
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
    except LLMQuotaExceededError as e:
        raise APIException(code='AI_QUOTA_EXCEEDED', http_status=status.HTTP_429_TOO_MANY_REQUESTS, message=str(e))
    except AIError as e:
        raise APIException(code='AI_SERVICE_ERROR', http_status=status.HTTP_503_SERVICE_UNAVAILABLE, message=str(e))

@router.post("/ai/executive-report", response_model=SuccessResponse[AIExecutiveReportResponseData])
async def generate_executive_report():
    try:
        from datetime import datetime
        result = await ai_service.generate_executive_report()
        return SuccessResponse(
            data=AIExecutiveReportResponseData(
                title=result.title,
                summary=result.summary,
                markdown=result.markdown,
                confidence=result.confidence,
                latency_ms=result.latency_ms,
                generated_at=datetime.utcnow().isoformat() + "Z"
            )
        )
    except LLMQuotaExceededError as e:
        raise APIException(code='AI_QUOTA_EXCEEDED', http_status=status.HTTP_429_TOO_MANY_REQUESTS, message=str(e))
    except AIError as e:
        raise APIException(code='AI_SERVICE_ERROR', http_status=status.HTTP_503_SERVICE_UNAVAILABLE, message=str(e))
