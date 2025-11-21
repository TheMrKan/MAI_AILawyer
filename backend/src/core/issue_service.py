from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import Issue
from typing import Optional

class IssueService:
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

    async def commit_issue(self, issue: Issue) -> Issue:
        await self.db.commit()
        await self.db.refresh(issue)
        return issue

    async def get_issue_by_id(self, issue_id: int, user_id: str) -> Optional[Issue]:
        result = await self.db.execute(
            select(Issue).where(
                Issue.id == issue_id,
                Issue.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def rollback_issue(self) -> None:
        await self.db.rollback()