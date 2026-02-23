from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.models.user import User
from src.schemas import ChatHistoryResponse, ChatRequest, ChatResponse
from src.workflows.health_workflow import run_workflow

router = APIRouter(
    prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)]
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await run_workflow(
        user_id=current_user.id,
        user_text=request.message,
        locale=request.locale,
        channel=request.channel,
    )

    return ChatResponse(
        response=result.get("assistant_text", "Sorry, I couldn't process your request."),
        intent=result.get("intent", "unknown"),
        locale=result.get("locale", request.locale),
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    from src.services.locusgraph.service import locusgraph_service

    query = f"conversation_turn person:{current_user.id}"
    results = await locusgraph_service.retrieve_context(
        query=query, limit=limit, context_ids=[f"person:{current_user.id}"]
    )

    conversations = []
    for memory in results:
        payload = memory.get("payload", {})
        data = payload.get("data", {})
        conversations.append(
            {
                "user_text": data.get("user_text", ""),
                "assistant_text": data.get("assistant_text", ""),
                "intent": data.get("intent", "unknown"),
                "timestamp": data.get("timestamp", ""),
            }
        )

    return ChatHistoryResponse(conversations=conversations, total_count=len(conversations))
