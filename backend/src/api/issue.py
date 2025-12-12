from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Self
import logging
from enum import Enum
from sqlalchemy import select

from src.core.chats.service import IssueChatService, GraphError
from src.application.provider import Provider, Scope
from src.core.chats.types import ChatMessage, MessageRole as DtoMessageRole
from src.api.deps import get_current_user, get_scope, get_db_session
from src.core.results.iface import IssueResultFileStorageABC
from src.core.issue_service import IssueService
from src.exceptions import ExternalRateLimitException
from src.core.users.types import UserInfo
from src.storage.sql.models import Issue


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/issue")


def __should_message_be_returned(dto: ChatMessage) -> bool:
    """
    Исключает системные сообщения из выдачи
    """
    return dto.role in (DtoMessageRole.USER, DtoMessageRole.AI)


class MessageRole(Enum):
    USER = "user"
    AI = "ai"


class MessageSchema(BaseModel):
    role: MessageRole
    text: str

    @classmethod
    def from_dto(cls, dto: ChatMessage) -> Self:
        assert dto.role in (DtoMessageRole.USER, DtoMessageRole.AI), f"Only User and AI messages are allowed (got '{dto.role}')"
        return {"text": dto.text,
                "role": MessageRole.USER.value if dto.role == DtoMessageRole.USER else MessageRole.AI.value}


class ChatStateSchema(BaseModel):
    new_messages: list[MessageSchema]
    is_ended: bool
    """
    Чат завершен, новые сообщения отправлять нельзя.
    """
    success: bool
    """
    True, если чат завершен генерацией документа.
    False, если пользователь отказался от продолжения, агент не нашел проблемы и т. д.
    """


@router.get('/{issue_id}/chat/')
async def get_issue_messages(
        issue_id: int,
        scope: Scope = Depends(get_scope),
        db: AsyncSession = Depends(get_db_session),
) -> ChatStateSchema:
    """
    Возвращает историю сообщений в чате обращения. Также возвращает is_ended и success.
    """

    scope.set_scoped_value(db, AsyncSession)

    try:
        issue = await scope[IssueService].get_issue_by_id(issue_id)

        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        state = await scope[IssueChatService].get_state(issue_id)
        new_messages = [
            MessageSchema.from_dto(message)
            for message in state.messages
            if __should_message_be_returned(message)
        ]
        return ChatStateSchema(new_messages=new_messages, is_ended=state.is_ended, success=state.success)

    except Exception as e:
        logger.exception("Error getting issue messages", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get messages")


class IssueSchema(BaseModel):
    issue_id: int
    created_at: str


class IssueCreateRequestSchema(BaseModel):
    text: str


@router.post('/create/')
async def create_issue(
        issue_data: IssueCreateRequestSchema,
        scope: Scope = Depends(get_scope),
        db: AsyncSession = Depends(get_db_session),
        current_user=Depends(get_current_user)
) -> IssueSchema:
    """
    Создает новый issue в БД и чат к нему.
    Сразу обрабатывает первое сообщение и возвращает ответ агента.
    Возвращает новую историю сообщений начиная с переданного message.
    :return:
    """

    scope.set_scoped_value(db, AsyncSession)

    issue_service = scope[IssueService]
    try:
        new_issue = await issue_service.create_issue(issue_data.text, current_user.id if current_user else None)
        chat_service = scope[IssueChatService]
        await chat_service.process_new_user_message(new_issue.id, issue_data.text)
        logger.info(f"New issue created: {new_issue.text}")

    except ExternalRateLimitException as e:
        logger.exception("Rate limit", exc_info=e)
        raise HTTPException(status_code=429, detail="Ограничение на внешнем сервисе")
    except Exception as e:
        logger.exception(f"Failed to create issue: {e}")
        raise HTTPException(status_code=500, detail="Failed to create issue")

    created_at = new_issue.created_at.strftime("%Y-%m-%d %H:%M:%S")

    return IssueSchema(
        issue_id=new_issue.id,
        created_at=created_at
    )


class AddUserMessageSchema(BaseModel):
    text: str


@router.post('/{issue_id}/chat/')
async def chat(
        issue_id: int,
        message: AddUserMessageSchema,
        provider: Annotated[Provider, Depends(Provider)]
) -> ChatStateSchema:
    """
    Добавляет новое сообщение в существующий чат и возвращает ответ агента.
    Возвращает новую историю сообщений начиная с переданного message.
    """
    try:
        chat_service = provider[IssueChatService]
        state = await chat_service.process_new_user_message(issue_id, message.text)
        new_messages = [MessageSchema.from_dto(message) for message in state.messages if __should_message_be_returned(message)]

    except GraphError as e:
        logger.exception("Graph error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalRateLimitException as e:
        logger.exception("Rate limit", exc_info=e)
        raise HTTPException(status_code=429, detail="Ограничение на внешнем сервисе")
    except Exception as e:
        logger.exception("Internal error", exc_info=e)
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return ChatStateSchema(new_messages=new_messages, is_ended=state.is_ended, success=state.success)


@router.get('/{issue_id}/download/')
async def download_issue_file(
        issue_id: int,
        scope: Annotated[Scope, Depends(get_scope)],
        db: AsyncSession = Depends(get_db_session),
        current_user: UserInfo = Depends(get_current_user)
):
    """
    Отдает выходной файл обращения в формате docx.
    """
    scope.set_scoped_value(db, AsyncSession)

    issue_service = scope[IssueService]
    try:
        issue = await issue_service.get_issue_by_id(issue_id)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        if not issue_service.can_download_result(issue, current_user):
            raise HTTPException(status_code=403, detail="Access denied")

        file = scope[IssueResultFileStorageABC].read_issue_result_file(issue_id)
        return StreamingResponse(
            file,
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

@router.get('/user/documents/')
async def get_user_documents(
        current_user: UserInfo = Depends(get_current_user),
        scope: Scope = Depends(get_scope),
        db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """
    Возвращает список документов пользователя.
    """
    logger.info(f"Getting documents for user: {current_user.id if current_user else 'None'}")

    scope.set_scoped_value(db, AsyncSession)

    if not current_user:
        logger.warning("User not authenticated")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        logger.info(f"Querying issues for user_id: {current_user.id}")
        result = await db.execute(
            select(Issue).where(
                Issue.user_id == current_user.id
            ).order_by(Issue.created_at.desc())
        )
        issues = result.scalars().all()

        logger.info(f"Found {len(issues)} issues for user")

        documents = []
        for issue in issues:

            try:
                chat_state = await scope[IssueChatService].get_state(issue.id)

                if chat_state.is_ended and chat_state.success:
                    status = "completed"
                elif chat_state.is_ended and not chat_state.success:
                    status = "error"
                else:
                    status = "draft"
            except KeyError as e:
                logger.debug(f"Chat not found for issue {issue.id}: {e}")
                status = "draft"
            except Exception as e:
                logger.warning(f"Error getting chat state for issue {issue.id}: {str(e)[:100]}")
                status = "draft"

            if issue.text:
                clean_text = ' '.join(issue.text.split())
                title = clean_text[:50] + "..." if len(clean_text) > 50 else clean_text
            else:
                title = f"Обращение #{issue.id}"

            documents.append({
                "id": issue.id,
                "issue_id": issue.id,
                "title": title,
                "status": status,
                "date": issue.created_at.strftime("%Y-%m-%d"),
                "created_at": issue.created_at.isoformat(),
                "text_preview": issue.text[:100] + "..." if len(issue.text) > 100 else issue.text
            })

        logger.info(f"Returning {len(documents)} documents")
        return documents

    except Exception as e:
        logger.exception(f"Error getting user documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")