from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ChatRole(StrEnum):
    user = "user"
    assistant = "assistant"


class ChatMessageCreate(BaseModel):
    role: ChatRole
    content: str


class ChatMessage(BaseModel):
    role: ChatRole
    content: str
    timestamp: datetime


class ChatHistory(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessageCreate] = Field(default_factory=list, max_length=50)


class ChatResponse(BaseModel):
    role: ChatRole = ChatRole.assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
