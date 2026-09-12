from fastapi import APIRouter, HTTPException

from app.api.dependencies import FactoryOperator
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send")
async def send_message(
    request: ChatRequest,
    current_user: FactoryOperator,
) -> ChatResponse:
    """Send a message to the chatbot and get a response."""
    try:
        return await chat_service.send_message(request)
    except chat_service.ChatConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except chat_service.ChatProviderError as exc:
        status_code = 429 if exc.status_code == 429 else 502
        raise HTTPException(status_code=status_code, detail=exc.detail) from exc
