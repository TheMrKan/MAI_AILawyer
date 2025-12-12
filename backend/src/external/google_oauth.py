import httpx
import secrets
import time

from src.core.users.iface import OAuthProviderABC
from src.core.users.types import UserSSOInfo
from src.config import settings
from src.application.provider import Registerable, Provider, Singleton


class GoogleOAuth(OAuthProviderABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        google_oauth = cls()
        provider.register(OAuthProviderABC, Singleton(google_oauth))
        provider.register(GoogleOAuth, Singleton(google_oauth))

    AUTH_STATE_TTL = 600

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = f"{settings.BACKEND_URL}/auth/google/callback"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.states = {}

    def generate_state(self) -> str:
        state = secrets.token_urlsafe(32)
        self.states[state] = time.time()
        return state

    def validate_state(self, state: str) -> bool:
        if state not in self.states:
            return False

        created_time = self.states[state]
        if time.time() - created_time >= self.AUTH_STATE_TTL:
            del self.states[state]
            return False

        del self.states[state]
        return True

    def get_authorization_url(self, state: str) -> str:
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "access_type": "offline",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def get_user_info(self, code: str) -> UserSSOInfo:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            tokens = token_response.json()
            access_token = tokens.get("access_token")

            if not access_token:
                raise ValueError(f"Google token error: {tokens}")

            user_info_response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            user_info = user_info_response.json()

            if not isinstance(user_info, dict):
                raise ValueError(f"Invalid userinfo response: {user_info}")

            if "email" not in user_info or "sub" not in user_info:
                raise ValueError(f"Incomplete userinfo: {user_info}")

            return UserSSOInfo(
                email=user_info["email"],
                sso_provider="google",
                sso_id=user_info["sub"],
                first_name=user_info.get("given_name", ""),
                last_name=user_info.get("family_name", ""),
                avatar_url=user_info.get("picture"),
            )

