from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Simple request/response schemas for conversation engine
class MessageSchema(BaseModel):
    id: str
    sender_id: str
    sender_type: str  # "user", "agent", "system", "ai"
    content: str
    timestamp: datetime

class ConversationSchema(BaseModel):
    id: str
    tenant_id: str
    status: str  # "open", "snoozed", "resolved"
    channel: str  # "whatsapp", "instagram", "web", "email"
    created_at: datetime
    messages: List[MessageSchema] = []

class CreateConversationRequest(BaseModel):
    channel: str = "web"
    tenant_id: str

class SendMessageRequest(BaseModel):
    sender_id: str
    sender_type: str
    content: str

# Mock local storage for the skeleton
MOCK_CONVERSATIONS = {}

@router.post("/", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
async def create_conversation(req: CreateConversationRequest):
    cid = f"conv_{len(MOCK_CONVERSATIONS) + 1}"
    new_conv = ConversationSchema(
        id=cid,
        tenant_id=req.tenant_id,
        status="open",
        channel=req.channel,
        created_at=datetime.utcnow()
    )
    MOCK_CONVERSATIONS[cid] = new_conv
    return new_conv

@router.get("/", response_model=List[ConversationSchema])
async def list_conversations(tenant_id: str):
    return [c for c in MOCK_CONVERSATIONS.values() if c.tenant_id == tenant_id]

@router.get("/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(conversation_id: str):
    if conversation_id not in MOCK_CONVERSATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )
    return MOCK_CONVERSATIONS[conversation_id]

@router.post("/{conversation_id}/messages", response_model=MessageSchema)
async def send_message(conversation_id: str, req: SendMessageRequest):
    if conversation_id not in MOCK_CONVERSATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )
    
    conv = MOCK_CONVERSATIONS[conversation_id]
    msg_id = f"msg_{len(conv.messages) + 1}"
    new_msg = MessageSchema(
        id=msg_id,
        sender_id=req.sender_id,
        sender_type=req.sender_type,
        content=req.content,
        timestamp=datetime.utcnow()
    )
    conv.messages.append(new_msg)
    return new_msg
