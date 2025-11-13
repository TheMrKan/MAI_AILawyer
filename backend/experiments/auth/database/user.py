from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.experiments.auth.models.user import User
from backend.experiments.auth.schemas.user import UserCreate
from backend.experiments.auth.core.interface import IUserRepository
import uuid
from typing import Optional


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, AttributeError):
            return None

        result = await self.db.execute(select(User).where(User.id == user_uuid))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_sso(self, sso_provider: str, sso_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.sso_provider == sso_provider,
                    User.sso_id == sso_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            sso_provider=user_data.sso_provider,
            sso_id=user_data.sso_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_or_create(self, user_data: UserCreate) -> User:
        user = await self.get_by_sso(user_data.sso_provider, user_data.sso_id)
        if user:
            return user


        try:
            return await self.create(user_data)
        except Exception as e:
            await self.db.rollback()

            user = await self.get_by_email(user_data.email)
            if user:
                user.sso_provider = user_data.sso_provider
                user.sso_id = user_data.sso_id
                if user_data.first_name and not user.first_name:
                    user.first_name = user_data.first_name
                if user_data.last_name and not user.last_name:
                    user.last_name = user_data.last_name


                await self.db.commit()
                await self.db.refresh(user)
                return user
            raise e