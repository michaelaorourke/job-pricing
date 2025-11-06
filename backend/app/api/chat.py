"""
Chat API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import uuid
from datetime import datetime

from app.models.database import get_db
from app.models.conversation import Conversation
from app.models.job_analysis import JobAnalysis
from app.schemas.chat import ChatMessage, ChatSession
from app.services.openai_service import OpenAIService

router = APIRouter()

@router.post("/session", response_model=ChatSession)
async def create_chat_session(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Create a new chat session for a job"""

    # Verify job exists
    job = db.query(JobAnalysis).filter(JobAnalysis.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job analysis not found")

    # Create conversation
    session_id = str(uuid.uuid4())
    conversation = Conversation(
        session_id=session_id,
        job_analysis_id=job_id,
        messages=[],
        context={"job_title": job.job_title, "location": job.location}
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {"session_id": session_id, "job_id": job_id}

@router.post("/message")
async def send_message(
    session_id: str,
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""

    # Get conversation
    conversation = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get OpenAI response
    openai_service = OpenAIService()

    # Build message history
    messages = conversation.messages or []
    messages.append({"role": "user", "content": message.content})

    # Get response
    response = await openai_service.chat_completion(
        messages=messages,
        context=conversation.context
    )

    # Update conversation
    messages.append({"role": "assistant", "content": response})
    conversation.messages = messages
    conversation.last_message_at = datetime.utcnow()
    conversation.total_tokens_used += 100  # Estimate, should get from OpenAI

    db.commit()

    return {"response": response}

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""

    await websocket.accept()

    # Get conversation
    conversation = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .first()

    if not conversation:
        await websocket.send_text(json.dumps({"error": "Conversation not found"}))
        await websocket.close()
        return

    openai_service = OpenAIService()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            # Build message history
            messages = conversation.messages or []
            messages.append({"role": "user", "content": message["content"]})

            # Stream response
            response_text = ""
            async for chunk in openai_service.chat_completion_stream(
                messages=messages,
                context=conversation.context
            ):
                response_text += chunk
                await websocket.send_text(json.dumps({"chunk": chunk}))

            # Update conversation
            messages.append({"role": "assistant", "content": response_text})
            conversation.messages = messages
            conversation.last_message_at = datetime.utcnow()
            db.commit()

            # Send completion signal
            await websocket.send_text(json.dumps({"complete": True}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        await websocket.close()

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""

    conversation = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "session_id": session_id,
        "messages": conversation.messages,
        "context": conversation.context,
        "created_at": conversation.created_at
    }