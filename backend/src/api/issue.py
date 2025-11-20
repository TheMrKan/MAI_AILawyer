from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
from typing import Self, Annotated
import logging

from src.core.issue_chat_service import IssueChatService, GraphError
from src.application.provider import Provider
from src.dto.messages import ChatMessage, MessageRole as DtoMessageRole
from src.database.models import Issue
from src.database.connection import get_db
from src.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/issue")


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

class IssueCreateSchema(BaseModel):
    text: str


@router.post('/create')
async def create_issue(
        issue_data: IssueCreateSchema,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    try:
        new_issue = Issue(
            text=issue_data.text,
            user_id=current_user.id
        )
        db.add(new_issue)
        await db.commit()
        await db.refresh(new_issue)
        logger.info(f"New issue created: {new_issue.text}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create issue")

    created_at = new_issue.created_at.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "issue_id": {"id": str(new_issue.id)},
        "created_at": created_at
    }

@router.post('/chat/{issue_id}/')
async def chat(issue_id: int, message: AddUserMessageSchema,
               provider: Annotated[Provider, Depends(Provider)]) -> ChatUpdateSchema:
    try:
        chat_service = provider[IssueChatService]
        dto_messages = await chat_service.process_new_user_message(issue_id, message.text)
        new_messages = [MessageSchema.from_dto(message) for message in dto_messages if __should_message_be_returned(message)]
        is_ended = await chat_service.is_ended(issue_id)
    except GraphError as e:
        logger.exception("Graph error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Internal error", exc_info=e)
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return ChatUpdateSchema(new_messages=new_messages, is_ended=is_ended)