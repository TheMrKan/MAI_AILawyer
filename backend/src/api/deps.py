from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.application.provider import Scope
from src.core.users.iface import AuthServiceABC, UserRepositoryABC
from src.core.users.types import UserInfo
from src.storage.sql.connection import get_session

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_db_session(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise


def get_scope() -> Scope:
    from src.application import provider
    return Scope(provider.global_provider)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        authorization: Optional[str] = Header(None),
        db: AsyncSession = Depends(get_db_session),
        scope: Scope = Depends(get_scope)
) -> UserInfo | None:
    scope.set_scoped_value(db, AsyncSession)

    token = None
    if credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        return None

    user_id = scope[AuthServiceABC].read_token(token)
    if not user_id:
        return None

    user = await scope[UserRepositoryABC].get_by_id(user_id)

    return user
