from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import traceback
from typing import Self

from src.core.graph_controller import GraphError
from src.core.container import Container
from src.dto.messages import ChatMessage, MessageRole as DtoMessageRole

router = APIRouter(prefix="/issue/{issue_id}")


class AddUserMessageSchema(BaseModel):
    text: str


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


@router.post('/chat/')
async def chat(issue_id: int, message: AddUserMessageSchema) -> ChatUpdateSchema:
    try:
        dto_messages = await Container.graph_controller.invoke_with_new_message(issue_id, message.text)
        new_messages = [MessageSchema.from_dto(message) for message in dto_messages]
    except GraphError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return ChatUpdateSchema(new_messages=new_messages)
