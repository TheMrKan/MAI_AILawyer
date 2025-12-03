from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.config import settings
from src.database.connection import get_db
from src.core.users.iface import AuthServiceABC, UserRepositoryABC
from src.external.google_oauth import GoogleOAuth
from src.application.provider import Provider, Scope


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/google")
async def google_auth(provider: Provider = Depends(Provider)):
    google_oauth = provider[GoogleOAuth]

    state = google_oauth.generate_state()
    auth_url = google_oauth.get_authorization_url(state)

    response = RedirectResponse(auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=600
    )
    return response


@router.get("/google/callback")
async def google_callback(
        request: Request,
        code: str = None,
        state: str = None,
        error: str = None,
        db: AsyncSession = Depends(get_db),
        scope: Scope = Depends(Scope)
):
    scope.set_scoped_value(db)

    if error:
        if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
            redirect_url = f"{settings.FRONTEND_URL}/auth/callback?error=auth_failed"
            return RedirectResponse(url=redirect_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state parameters"
        )

    cookie_state = request.cookies.get("oauth_state")

    google_oauth = scope[GoogleOAuth]
    if not cookie_state or not google_oauth.validate_state(cookie_state) or state != cookie_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    try:
        user_data = await google_oauth.get_user_info(code)
        user_repo = scope[UserRepositoryABC]
        user = await user_repo.get_or_create(user_data)
        token_response = scope[AuthServiceABC].create_token_response(user)

        response_data = {
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar_url": user.avatar_url
            }
        }

        if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
            import urllib.parse
            import json
            user_data_encoded = urllib.parse.quote(json.dumps(response_data))
            redirect_url = f"{settings.FRONTEND_URL}/auth/callback?data={user_data_encoded}"
            response = RedirectResponse(url=redirect_url)
        else:
            response = response_data

        response.delete_cookie("oauth_state")
        return response

    except ValueError as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/token/verify")
async def verify_token(token: str,
                       provider: Provider = Depends(Provider)):
    token_data = provider[AuthServiceABC].verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return {"valid": True, "user_id": token_data.user_id, "email": token_data.email}
