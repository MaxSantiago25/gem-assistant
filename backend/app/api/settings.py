from fastapi import APIRouter, Depends
from app.core.security import verify_island_token
from app.schemas.settings import SettingsUpdateRequest, SettingsResponse
from app.services.settings_service import settings_service

router = APIRouter()

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(token: str = Depends(verify_island_token)):
    current_settings = settings_service.get_settings()
    return {"settings": current_settings}

@router.put("/settings", response_model=SettingsResponse)
async def update_settings(payload: SettingsUpdateRequest, token: str = Depends(verify_island_token)):
    updated = settings_service.update_settings(payload.settings)
    return {"settings": updated}

