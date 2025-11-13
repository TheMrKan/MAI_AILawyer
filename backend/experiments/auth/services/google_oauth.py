import httpx
from auth.schemas.user import UserCreate
from auth.config import settings

class GoogleOAuth:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = f"{settings.BACKEND_URL}/auth/google/callback"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_authorization_url(self, state: str):
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

    async def get_user_info(self, code: str) -> UserCreate:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                }
            )

            if token_response.status_code != 200:
                raise ValueError("Failed to get access token")

            tokens = token_response.json()
            access_token = tokens.get("access_token")

            user_info_response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if user_info_response.status_code != 200:
                raise ValueError("Failed to get user info")

            user_info = user_info_response.json()

        return UserCreate(
            email=user_info["email"],
            sso_provider="google",
            sso_id=user_info["sub"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            avatar_url=user_info.get("picture")
        )

google_oauth = GoogleOAuth()