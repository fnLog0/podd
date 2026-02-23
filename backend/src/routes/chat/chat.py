"""Routes for chat functionality with LangGraph workflow integration."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import get_current_user
from src.schemas.chat import ChatHistoryResponse, ChatMessage, ChatRequest, ChatResponse
from src.services.locusgraph.service import locusgraph_service
from src.workflows.health_workflow import run_workflow

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(chat_request: ChatRequest, current_user=Depends(get_current_user)):
    """Send a chat message and get a response from the LangGraph workflow.

    This endpoint:
    1. Receives a user message
    2. Runs it through the LangGraph workflow (intent detection, context retrieval, agent execution)
    3. Returns the assistant's response
    4. Stores the conversation in LocusGraph for history tracking
    """
    user_id = str(current_user.id)

    # Run the LangGraph workflow
    try:
        workflow_result = await run_workflow(
            user_id=user_id,
            user_text=chat_request.message,
            locale=chat_request.locale,
            channel=chat_request.channel,
        )

        # Extract response data
        assistant_text = workflow_result.get("assistant_text", "Sorry, I couldn't process that.")
        intent = workflow_result.get("intent", "unknown")

        # Create chat event ID
        chat_event_id = locusgraph_service.new_id()

        # Store user message in LocusGraph
        user_message_event = {
            "event_kind": "observation",
            "context_id": f"chat:{chat_event_id}_user",
            "related_to": [f"person:{user_id}"],
            "payload": {
                "kind": "chat_message",
                "data": {
                    "role": "user",
                    "content": chat_request.message,
                    "locale": chat_request.locale,
                    "channel": chat_request.channel,
                    "user_id": user_id,
                    "timestamp": locusgraph_service.now(),
                },
            },
        }

        # Store assistant response in LocusGraph
        assistant_message_event = {
            "event_kind": "observation",
            "context_id": f"chat:{chat_event_id}_assistant",
            "related_to": [f"person:{user_id}", f"chat:{chat_event_id}_user"],
            "payload": {
                "kind": "chat_message",
                "data": {
                    "role": "assistant",
                    "content": assistant_text,
                    "intent": intent,
                    "locale": chat_request.locale,
                    "channel": chat_request.channel,
                    "user_id": user_id,
                    "timestamp": locusgraph_service.now(),
                },
            },
        }

        # Store events
        await locusgraph_service.store_event(**user_message_event)
        await locusgraph_service.store_event(**assistant_message_event)

        # Return response
        return ChatResponse(
            id=chat_event_id,
            user_id=user_id,
            user_message=chat_request.message,
            assistant_message=assistant_text,
            intent=intent,
            created_at=datetime.now(timezone.utc),
            metadata={
                "locale": chat_request.locale,
                "channel": chat_request.channel,
                "workflow_result": {
                    k: v for k, v in workflow_result.items()
                    if k not in ["assistant_text", "intent"]
                },
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Failed to process chat message",
                "detail": str(e),
            },
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    limit: int = 50,
    offset: int = 0,
    current_user=Depends(get_current_user),
):
    """Get chat history for the current user.

    Returns all chat messages (both user and assistant) in chronological order.
    """
    user_id = str(current_user.id)

    # Query chat messages from LocusGraph
    query = f"chat messages user {user_id}"
    memories = await locusgraph_service.retrieve_context(query=query, limit=limit * 2)

    # Process memories into chat messages
    messages = []
    for memory in memories:
        payload = memory.get("payload", {})
        data = payload.get("data", {})

        if data.get("user_id") == user_id:
            messages.append(
                ChatMessage(
                    id=memory.get("event_id", ""),
                    user_id=user_id,
                    role=data.get("role", "user"),
                    content=data.get("content", ""),
                    created_at=datetime.fromisoformat(data.get("timestamp", memory.get("timestamp", ""))),
                    channel=data.get("channel", "text"),
                )
            )

    # Sort messages by created_at
    messages.sort(key=lambda m: m.created_at)

    # Apply pagination
    paginated_messages = messages[offset:offset + limit]

    return ChatHistoryResponse(
        user_id=user_id,
        messages=paginated_messages,
        total_count=len(messages),
        retrieved_at=datetime.now(timezone.utc),
    )
