from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from pydantic import BaseModel, ConfigDict
from pydantic.types import UUID4
from typing import Optional

from src.api.deps import get_current_user, get_scope
from src.core.users.types import UserInfo
from src.core.users.types import UserInfo
from src.core.issue_service import IssueService
from src.core.chats.service import IssueChatService
from src.application.provider import Scope
from src.core.users.iface import AuthServiceABC


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    email: str
    first_name: str
    last_name: str
    avatar_url: str
    auth_token: Optional[str] = None

@router.get("/me", response_model=ProfileResponse | None)
async def get_my_profile(
    request: Request,
    current_user: UserInfo = Depends(get_current_user),
    scope: Scope = Depends(get_scope),
):
    if not current_user:
        raise HTTPException(status_code=401)

    profile = ProfileResponse.model_validate(current_user)

    auth_header = request.headers.get("authorization")
    has_token = auth_header and auth_header.startswith("Bearer ")

    if not has_token:
        auth_service = scope[AuthServiceABC]
        auth_token = auth_service.authenticate(current_user)

        profile.auth_token = auth_token.access_token

    return profile




@router.get("/documents/")
async def get_user_documents(
    current_user: UserInfo = Depends(get_current_user),
    scope: Scope = Depends(get_scope),
) -> list[dict]:
    """
    Возвращает список документов пользователя.
    """
    logger.info(
        "Getting documents for user: %s",
        current_user.id if current_user else "None"
    )

    if not current_user:
        logger.warning("User not authenticated")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        issue_service = scope[IssueService]
        chat_service = scope[IssueChatService]

        issues = await issue_service.get_user_issues(current_user.id)

        logger.info("Found %s issues for user", len(issues))

        documents: list[dict] = []

        for issue in issues:
            try:
                chat_state = await chat_service.get_state(issue.id)

                if chat_state.is_ended and chat_state.success:
                    status = "completed"
                elif chat_state.is_ended and not chat_state.success:
                    status = "error"
                else:
                    status = "draft"

            except KeyError:
                status = "draft"
            except Exception as e:
                logger.warning(
                    "Error getting chat state for issue %s: %s",
                    issue.id,
                    str(e)[:100],
                )
                status = "draft"

            if issue.text:
                clean_text = " ".join(issue.text.split())
                title = (
                    clean_text[:50] + "..."
                    if len(clean_text) > 50
                    else clean_text
                )
            else:
                title = f"Обращение #{issue.id}"

            documents.append(
                {
                    "id": issue.id,
                    "issue_id": issue.id,
                    "title": title,
                    "status": status,
                    "date": issue.created_at.strftime("%Y-%m-%d"),
                    "created_at": issue.created_at.isoformat(),
                }
            )

        logger.info("Returning %s documents", len(documents))
        return documents

    except Exception as e:
        logger.exception("Error getting user documents")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get documents: {str(e)}",
        )
