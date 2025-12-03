import os
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock
import asyncpg

from src.main import app
from src.database.connection import get_db
from src.database.base import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def create_test_database():
    if "TEST_DATABASE_URL" in os.environ:
        yield
        return

    try:
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
        try:
            await conn.execute("DROP DATABASE IF EXISTS test_db")
        except:
            pass
        await conn.execute("CREATE DATABASE test_db")
        await conn.close()
    except Exception as e:
        pytest.skip(f"Cannot create test database: {e}")

    yield

    try:
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
        await conn.execute("DROP DATABASE IF EXISTS test_db")
        await conn.close()
    except:
        pass


@pytest.fixture(scope="function")
async def test_db(create_test_database):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
def client(test_db):
    async def override_get_db():
        try:
            yield test_db
        finally:
            await test_db.close()

    app.dependency_overrides[get_db] = override_get_db
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