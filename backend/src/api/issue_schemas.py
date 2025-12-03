from pydantic import BaseModel
from typing import Self
from enum import Enum

from src.dto.messages import ChatMessage, MessageRole as DtoMessageRole


class MessageRole(Enum):
    USER = "user"
    AI = "ai"


class MessageSchema(BaseModel):
    role: MessageRole
    text: str

    @classmethod
    def from_dto(cls, dto: ChatMessage) -> Self:
        assert dto.role in (DtoMessageRole.USER, DtoMessageRole.AI), f"Only User and AI messages are allowed (got '{dto.role}')"
        return {"text": dto.text, "role": MessageRole.USER.value if dto.role == DtoMessageRole.USER else MessageRole.AI.value}


class ChatUpdateSchema(BaseModel):
    new_messages: list[MessageSchema]
    is_ended: bool
    success: bool


class IssueCreateResponseSchema(BaseModel):
    issue_id: int
    created_at: str


class IssueCreateRequestSchema(BaseModel):
    text: str


class AddUserMessageSchema(BaseModel):
    text: str