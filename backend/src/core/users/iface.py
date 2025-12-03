from abc import ABC, abstractmethod
from typing import Optional, Dict

from src.api.schemas import UserCreate


class OAuthProviderABC(ABC):
    @abstractmethod
    async def get_user_info(self, code: str) -> UserCreate:
        pass

    @abstractmethod
    def get_authorization_url(self) -> str:
        pass


class UserRepositoryABC(ABC):
    @abstractmethod
    async def get_by_email(self, email: str):
        pass

    @abstractmethod
    async def get_by_sso(self, sso_provider: str, sso_id: str):
        pass

    @abstractmethod
    async def create(self, user_data: UserCreate):
        pass


class AuthServiceABC(ABC):
    @abstractmethod
    def create_access_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict]:
        pass