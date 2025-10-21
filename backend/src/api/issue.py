from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import Self
import logging

from src.core.graph_controller import GraphError
from src.core.container import Container
from src.dto.messages import ChatMessage, MessageRole as DtoMessageRole


logger = logging.getLogger(__name__)

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
    is_ended: bool


def __should_message_be_returned(dto: ChatMessage) -> bool:
    return dto.role in (DtoMessageRole.USER, DtoMessageRole.AI)


@router.post('/chat/')
async def chat(issue_id: int, message: AddUserMessageSchema) -> ChatUpdateSchema:
    try:
        dto_messages = await Container.graph_controller.invoke_with_new_message(issue_id, message.text)
        new_messages = [MessageSchema.from_dto(message) for message in dto_messages if __should_message_be_returned(message)]
        is_ended = await Container.graph_controller.is_ended(issue_id)
    except GraphError as e:
        logger.exception("Graph error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Internal error", exc_info=e)
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return ChatUpdateSchema(new_messages=new_messages, is_ended=is_ended)
