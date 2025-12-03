from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.application.provider import Scope
from src.core.users.iface import AuthServiceABC, UserRepositoryABC
from src.storage.sql.connection import get_db

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def get_scope() -> Scope:
    from src.application import provider
    return Scope(provider.global_provider)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        authorization: Optional[str] = Header(None),
        db: AsyncSession = Depends(get_db),
        scope: Scope = Depends(get_scope)
):
    scope.set_scoped_value(db, AsyncSession)

    token = None
    if credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        return None

    token_data = scope[AuthServiceABC].verify_token(token)
    if not token_data:
        return None

    user_repo = scope[UserRepositoryABC]
    user = await user_repo.get_by_id(token_data.user_id)

    return user
