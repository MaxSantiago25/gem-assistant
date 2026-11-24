from typing import Optional
from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_island_token(x_island_token: Optional[str] = Header(None, alias="X-Island-Token")):
    """
    Verifica que la petición incluya el token de sesión emitido por Tauri (CA-3 de Spec 002).
    Si falta o es inválido, responde 401 Unauthorized.
    """
    if not x_island_token or x_island_token != settings.session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Token de sesión inválido o ausente"}}
        )
    return x_island_token
