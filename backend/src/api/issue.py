from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
from typing import Self, Annotated
import logging

from src.core.issue_chat_service import IssueChatService, GraphError
from src.application.provider import Provider
from src.dto.messages import ChatMessage, MessageRole as DtoMessageRole
from src.database.connection import get_db
from src.api.deps import get_current_user
from src.core.results.iface import IssueResultFileStorageABC

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


@router.get('/{issue_id}/download/')
async def download_issue_file(
        issue_id: int,
        provider: Annotated[Provider, Depends(Provider)],
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    try:
        storage = provider[IssueResultFileStorageABC]

        issue = await db.get(Issue, issue_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        if issue.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        with storage.read_issue_result_file(str(issue_id)) as file:
            file_content = file.read()

        return StreamingResponse(
            iter([file_content]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=issue_{issue_id}_result.docx"
            }
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found for this issue")
    except Exception as e:
        logger.exception("Error downloading issue file", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to download file")