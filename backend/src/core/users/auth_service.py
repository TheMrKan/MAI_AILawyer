import datetime
from jose import jwt, JWTError

from src.config import settings
from src.core.users.types import UserInfo, AuthToken
from src.core.users.iface import AuthServiceABC
from src.application.provider import Registerable, Provider, Singleton


class AuthService(AuthServiceABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        provider.register(AuthServiceABC, Singleton(cls()))

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.jwt_algorithm = settings.ALGORITHM
        self.jwt_token_expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def authenticate(self, user: UserInfo) -> AuthToken:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=self.jwt_token_expiration)
        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "exp": int(expire.timestamp()),
            "type": "access",
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.jwt_algorithm)

        return AuthToken(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=self.jwt_token_expiration * 60,
        )

    def read_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
        except JWTError:
            return None

        if payload.get("type") != "access":
            return None

        expire: int = payload.get("exp", 0)
        if expire < int(datetime.datetime.now(datetime.UTC).timestamp()):
            return None

        user_id: str = payload.get("sub")
        return user_id
