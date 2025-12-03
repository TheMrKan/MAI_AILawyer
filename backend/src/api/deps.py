from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.application.provider import Provider
from src.core.users.iface import AuthServiceABC
from src.database.user import UserRepository
from src.database.connection import get_db

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        authorization: Optional[str] = Header(None),
        db: AsyncSession = Depends(get_db),
        provider: Provider = Depends(Provider)
):
    token = None
    if credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        return None

    token_data = provider[AuthServiceABC].verify_token(token)
    if not token_data:
        return None

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(token_data.user_id)

    return user


async def get_current_active_user(
        current_user=Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user