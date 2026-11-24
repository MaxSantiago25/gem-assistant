from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_island_token
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationDetailResponse
)
from app.services.conversation_service import conversation_service

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(token: str = Depends(verify_island_token)):
    return conversation_service.list_conversations()

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate, token: str = Depends(verify_island_token)):
    return conversation_service.create_conversation(title=payload.title, provider=payload.provider)

@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation(conv_id: str, token: str = Depends(verify_island_token)):
    detail = conversation_service.get_conversation_detail(conv_id)
    if not detail:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Conversación no encontrada"}})
    return detail

@router.post("/conversations/{conv_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(conv_id: str, payload: MessageCreate, token: str = Depends(verify_island_token)):
    msg = conversation_service.append_message(conv_id=conv_id, role=payload.role, content=payload.content)
    if not msg:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Conversación no encontrada"}})
    return msg

