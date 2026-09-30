from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.ai.chat import process_chat_message

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    current_location: Optional[str] = None
    session_id: Optional[str] = "default-session"

@router.post("/")
def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    result = process_chat_message(
        session_id=req.session_id,
        message=req.message,
        current_location=req.current_location
    )
    
    return result
