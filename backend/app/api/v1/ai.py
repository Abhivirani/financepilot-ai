from fastapi import APIRouter
from backend.app.schemas.ai import AIExplainRequest, AIExplainResponseData
from backend.app.schemas.common import SuccessResponse

router = APIRouter()

@router.post("/ai/explain", response_model=SuccessResponse[AIExplainResponseData])
async def explain_exception(req: AIExplainRequest):
    return SuccessResponse(
        data=AIExplainResponseData(
            explanation=f"Explanation for {req.exception_id}: This is a placeholder backend response. AI functionality is not yet implemented."
        )
    )
