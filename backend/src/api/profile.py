from fastapi import APIRouter, Depends
import logging
from pydantic import BaseModel
from pydantic.types import UUID4

from src.api.deps import get_current_user
from src.core.users.types import UserInfo


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileResponse(BaseModel):
    id: UUID4
    email: str
    first_name: str
    last_name: str
    avatar_url: str


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
        current_user: UserInfo = Depends(get_current_user)
):
    return ProfileResponse.model_validate(current_user)
