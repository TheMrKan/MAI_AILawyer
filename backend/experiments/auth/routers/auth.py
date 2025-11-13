from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.experiments.auth.config import settings
from backend.experiments.auth.database.connection import get_db
from backend.experiments.auth.services.google_oauth import google_oauth
from backend.experiments.auth.services.auth import auth_service
from backend.experiments.auth.services.state_service import state_service
from backend.experiments.auth.repositories.user import UserRepository
from backend.experiments.auth.dependencies.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/google")
async def google_auth():
    state = state_service.generate_state()
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
):
    if error:
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
    if not cookie_state or not state_service.validate_state(cookie_state) or state != cookie_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    try:
        user_data = await google_oauth.get_user_info(code)
        user_repo = UserRepository(db)
        user = await user_repo.get_or_create(user_data)
        token_response = auth_service.create_token_response(user)

        return {
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
async def verify_token(token: str):
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return {"valid": True, "user_id": token_data.user_id, "email": token_data.email}

@router.get("/me")
async def get_current_user(current_user=Depends(get_current_user)):
    return current_user

@router.get("/test")
async def test_auth():
    return {"message": "Auth router working"}