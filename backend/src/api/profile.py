from fastapi import APIRouter, Depends

from src.api.deps import get_current_user
from src.storage.sql.models import User
from src.api.schemas import ProfileResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
        current_user: User = Depends(get_current_user)
):
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )
