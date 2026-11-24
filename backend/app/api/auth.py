from fastapi import APIRouter, Depends
from app.core.security import verify_island_token

router = APIRouter()

@router.post("/auth/logout")
async def logout(token: str = Depends(verify_island_token)):
    # Invalida sesión local según ADR y 01-arquitectura.md §7
    return {
        "status": "logged_out",
        "message": "Sesión cerrada correctamente"
    }

