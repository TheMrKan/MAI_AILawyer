from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid

from src.storage.sql.models import User
from src.core.users.iface import UserRepositoryABC
from src.core.users.types import UserInfo, UserSSOInfo


class UserRepository(UserRepositoryABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> UserInfo | None:
        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, AttributeError):
            return None

        result = await self.db.execute(select(User).where(User.id == user_uuid))
        db_user = result.scalar_one_or_none()
        return UserInfo.model_validate(db_user)

    async def get_by_email(self, email: str) -> UserInfo | None:
        result = await self.db.execute(select(User).where(User.email == email))
        db_user = result.scalar_one_or_none()
        return UserInfo.model_validate(db_user)

    async def get_by_sso(self, sso_provider: str, sso_id: str) -> UserInfo | None:
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.sso_provider == sso_provider,
                    User.sso_id == sso_id
                )
            )
        )
        db_user = result.scalar_one_or_none()
        return UserInfo.model_validate(db_user)

    async def create(self, user_data: UserSSOInfo) -> UserInfo:
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            sso_provider=user_data.sso_provider,
            sso_id=user_data.sso_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
        )
        self.db.add(user)
        await self.db.flush()
        return UserInfo.model_validate(user)

    async def get_or_create(self, user_data: UserSSOInfo) -> UserInfo:
        user = await self.get_by_sso(user_data.sso_provider, user_data.sso_id)
        if user:
            return user

        user = await self.get_by_email(user_data.email)
        if user:
            return user

        return await self.create(user_data)
