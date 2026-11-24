from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import verify_island_token
from app.agent.orchestrator import orchestrator
from app.services.conversation_service import conversation_service
from app.harness_ia.policy import PolicyError

router = APIRouter()


class ChatTurnRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=8000)
    mode: str = Field(default="auto")
    allow_cloud: bool = Field(default=False)


@router.post("/chat")
async def send_chat_message(payload: ChatTurnRequest, token: str = Depends(verify_island_token)):
    conv_id = payload.conversation_id
    if not conv_id:
        short_title = payload.message.strip()[:40]
        created = conversation_service.create_conversation(title=short_title, provider="llamacpp")
        conv_id = created["id"]
    else:
        existing = conversation_service.get_conversation_detail(conv_id)
        if not existing:
            short_title = payload.message.strip()[:40]
            created = conversation_service.create_conversation(title=short_title, provider="llamacpp")
            conv_id = created["id"]

    try:
        result = await orchestrator.process_chat_turn(
            conversation_id=conv_id,
            user_message=payload.message,
            mode=payload.mode,
            allow_cloud=payload.allow_cloud
        )
        result["conversation_id"] = conv_id
        return result
    except PolicyError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": pe.code, "message": pe.message}}
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": str(ve), "message": "Conversación no encontrada"}}
        )


@router.post("/actions/{batch_id}/confirm")
async def confirm_action_batch(batch_id: str, token: str = Depends(verify_island_token)):
    try:
        return await orchestrator.confirm_pending_batch(batch_id)
    except PolicyError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": pe.code, "message": pe.message}}
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "LOTE_NO_ENCONTRADO", "message": "El lote de acción ya fue procesado o no existe"}}
        )


@router.post("/actions/{batch_id}/reject")
async def reject_action_batch(batch_id: str, token: str = Depends(verify_island_token)):
    try:
        return orchestrator.reject_pending_batch(batch_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "LOTE_NO_ENCONTRADO", "message": "El lote de acción ya fue procesado o no existe"}}
        )


@router.post("/actions/{batch_id}/undo")
async def undo_action_batch(batch_id: str, token: str = Depends(verify_island_token)):
    try:
        return orchestrator.undo_executed_batch(batch_id)
    except PolicyError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": pe.code, "message": pe.message}}
        )

