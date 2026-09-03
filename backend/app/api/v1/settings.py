from fastapi import APIRouter, Depends

from backend.app.schemas.settings import SettingsData
from backend.app.schemas.common import SuccessResponse
from backend.app.services.settings_service import SettingsService

router = APIRouter()

def get_settings_service() -> SettingsService:
    return SettingsService()

@router.get("/settings", response_model=SuccessResponse[SettingsData])
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    result = await settings_service.get_settings()
    return SuccessResponse(data=result)

@router.put("/settings", response_model=SuccessResponse[SettingsData])
async def update_settings(
    settings_data: SettingsData,
    settings_service: SettingsService = Depends(get_settings_service)
):
    result = await settings_service.update_settings(settings_data)
    return SuccessResponse(data=result)
