"""
Chat API routes for AI-powered Todo Chatbot
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from models import Conversation, Message, UserResponse
from db import get_session, engine
from agents.todo_agent import process_chat_message
from middleware.auth import get_current_user


router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process a chat message for a user using the AI agent
    """
    # Verify that the authenticated user matches the user_id in the path
    # Note: current_user is a dict, so access id as current_user["id"]
    if "id" not in current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )
    if str(current_user["id"]) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's chat"
        )

    # Get or create conversation
    conversation_id = request.conversation_id

    if conversation_id is None:
        # Create a new conversation
        conversation = Conversation(user_id=user_id)
        with Session(engine) as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            conversation_id = conversation.id
    else:
        # Verify the conversation belongs to the user
        with Session(engine) as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation or str(conversation.user_id) != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to access this conversation"
                )

    # Fetch conversation history
    with Session(engine) as session:
        # Get messages for this conversation ordered by creation time
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        messages = session.exec(statement).all()

        # Format messages for the agent
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

    # Process the message with the AI agent
    try:
        result = process_chat_message(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

    # Store the user's message in the database
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        tool_calls=None  # User messages don't have tool calls
    )

    # Store the agent's response in the database with tool calls
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["response"],
        tool_calls=json.dumps(result["tool_calls"]) if result["tool_calls"] else None
    )

    with Session(engine) as session:
        session.add(user_message)
        session.add(assistant_message)
        session.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        response=result["response"],
        tool_calls=result["tool_calls"]
    )


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    created_at: str
    updated_at: Optional[str]


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    tool_calls: Optional[str]
    created_at: str


@router.get("/{user_id}/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all conversations for a user
    """
    if "id" not in current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )
    if str(current_user["id"]) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's conversations"
        )

    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.user_id == int(user_id)
        ).order_by(Conversation.created_at.desc())
        conversations = session.exec(statement).all()

        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat() if conv.updated_at else None
            )
            for conv in conversations
        ]


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all messages for a specific conversation
    """
    if "id" not in current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )
    if str(current_user["id"]) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's conversations"
        )

    with Session(engine) as session:
        # Verify the conversation belongs to the user
        conversation = session.get(Conversation, conversation_id)
        if not conversation or str(conversation.user_id) != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this conversation"
            )

        # Get messages for this conversation ordered by creation time
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        messages = session.exec(statement).all()

        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]


@router.get("/2/conversations", response_model=List[ConversationResponse])
async def get_user_conversations_v2(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all conversations for the current user (v2 API)
    """
    if "id" not in current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )

    user_id = str(current_user["id"])

    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.user_id == int(user_id)
        ).order_by(Conversation.created_at.desc())
        conversations = session.exec(statement).all()

        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat() if conv.updated_at else None
            )
            for conv in conversations
        ]

@router.post("/2/chat", response_model=ChatResponse)
async def chat_v2(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process a chat message for the current user (v2 API)
    """
    if "id" not in current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )

    user_id = str(current_user["id"])

    # Get or create conversation
    conversation_id = request.conversation_id

    if conversation_id is None:
        # Create a new conversation
        conversation = Conversation(user_id=user_id)
        with Session(engine) as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            conversation_id = conversation.id
    else:
        # Verify the conversation belongs to the user
        with Session(engine) as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation or str(conversation.user_id) != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to access this conversation"
                )

    # Fetch conversation history
    with Session(engine) as session:
        # Get messages for this conversation ordered by creation time
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        messages = session.exec(statement).all()

        # Format messages for the agent
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

    # Process the message with the AI agent
    try:
        result = process_chat_message(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

    # Store the user's message in the database
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        tool_calls=None  # User messages don't have tool calls
    )

    # Store the agent's response in the database with tool calls
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["response"],
        tool_calls=json.dumps(result["tool_calls"]) if result["tool_calls"] else None
    )

    with Session(engine) as session:
        session.add(user_message)
        session.add(assistant_message)
        session.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        response=result["response"],
        tool_calls=result["tool_calls"]
    )
