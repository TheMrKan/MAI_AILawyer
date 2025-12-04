from pydantic import BaseModel, ConfigDict
from pydantic.types import UUID4


class UserSSOInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    sso_provider: str
    sso_id: str
    first_name: str
    last_name: str
    avatar_url: str


class UserInfo(UserSSOInfo):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4


class AuthToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str
    expires_in: int

