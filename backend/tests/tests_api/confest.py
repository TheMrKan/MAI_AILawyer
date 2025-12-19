import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()

    session.get = AsyncMock()
    session.query = Mock(return_value=Mock(
        filter=Mock(return_value=Mock(
            first=AsyncMock()
        ))
    ))

    yield session


@pytest.fixture(scope="function")
def client(mock_db_session):
    from src.storage.sql.connection import get_session

    async def override_get_db():
        try:
            yield mock_db_session
        finally:
            await mock_db_session.close()

    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    user = Mock()
    user.id = "123e4567-e89b-12d3-a456-426614174000"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.avatar_url = "https://example.com/avatar.jpg"
    user.is_active = True
    user.created_at = "2024-01-01T00:00:00"
    user.sso_provider = "google"
    user.sso_id = "123456789"
    return user


@pytest.fixture
def mock_token():
    return {
        "access_token": "test_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "avatar_url": "https://example.com/avatar.jpg",
            "is_active": True,
            "sso_provider": "google",
            "created_at": "2024-01-01T00:00:00"
        }
    }


@pytest.fixture
def mock_user_repository(mock_user):
    with patch('src.api.routers.UserRepository') as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_or_create = AsyncMock(return_value=mock_user)
        mock_repo.return_value = mock_repo_instance
        yield mock_repo_instance