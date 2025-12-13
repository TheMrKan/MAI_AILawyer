from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.core.users.types import UserInfo
from src.storage.sql.models import Issue
from src.application.provider import Registerable, Provider, Transient


class IssueService(Registerable):
    """
    Смесь репозитория и сервиса, но вроде не критично. Не хочется раздувать код ради одной функции.
    Да, надо исправить, когда будет время.
    """

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        provider.register(IssueService, Transient(cls))

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_issue(self, text: str, user_id: str | None) -> Issue:
        new_issue = Issue(
            text=text,
            user_id=user_id
        )
        self.db.add(new_issue)
        await self.db.flush()
        return new_issue

    async def get_issue_by_id(self, issue_id: int) -> Optional[Issue]:
        result = await self.db.execute(
            select(Issue).where(
                Issue.id == issue_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_issues(self, user_id):
        result = await self.db.execute(
            select(Issue)
            .where(Issue.user_id == user_id)
            .order_by(Issue.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    def can_download_result(issue: Issue, user: UserInfo | None) -> bool:
        if not user:
            return False

        return issue.user_id == user.id
