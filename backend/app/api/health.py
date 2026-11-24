from fastapi import APIRouter
from app.connections.registry import registry

router = APIRouter()

@router.get("/health")
async def health_check():
    active_provider = registry.get_active()
    is_available = await active_provider.health() if active_provider else False

    return {
        "status": "ok",
        "service": "island-agent-backend",
        "version": "0.1.0",
        "provider": {
            "name": active_provider.name if active_provider else "none",
            "available": is_available
        }
    }
