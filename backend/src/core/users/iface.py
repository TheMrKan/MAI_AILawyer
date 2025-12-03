from abc import ABC, abstractmethod

from src.core.users.types import UserSSOInfo, UserInfo, AuthToken


class OAuthProviderABC(ABC):
    @abstractmethod
    async def get_user_info(self, code: str) -> UserSSOInfo:
        pass

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        pass


class UserRepositoryABC(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserInfo | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserInfo | None:
        pass

    @abstractmethod
    async def get_by_sso(self, sso_provider: str, sso_id: str) -> UserInfo | None:
        pass

    @abstractmethod
    async def create(self, user_data: UserSSOInfo) -> UserInfo:
        pass

    @abstractmethod
    async def get_or_create(self, user_data: UserSSOInfo) -> UserInfo:
        pass


class AuthServiceABC(ABC):

    @abstractmethod
    def authenticate(self, user: UserInfo) -> AuthToken:
        pass

    @abstractmethod
    def read_token(self, token: str) -> str | None:
        pass
