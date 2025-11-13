from datetime import datetime, timedelta
from jose import jwt, JWTError
from auth.config import settings
from auth.schemas.user import Token, UserResponse, TokenData
from auth.core.interface import IAuthService
from typing import Optional

class AuthService(IAuthService):
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.jwt_algorithm = settings.ALGORITHM
        self.jwt_token_expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, user_id: str, email: str) -> str:
        expires_delta = timedelta(minutes=self.jwt_token_expiration)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "access",
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.jwt_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])

            if payload.get("type") != "access":
                return None

            user_id: str = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None or email is None:
                return None

            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None

    def create_token_response(self, user):
        access_token = self.create_access_token(str(user.id), user.email)

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.jwt_token_expiration * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                sso_provider=user.sso_provider,
                is_active=user.is_active,
                created_at=user.created_at,
            )
        )


auth_service = AuthService()