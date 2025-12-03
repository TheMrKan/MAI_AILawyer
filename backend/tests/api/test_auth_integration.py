import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
import uuid

from src.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_auth_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "auth@example.com"
    user.first_name = "Auth"
    user.last_name = "User"
    user.avatar_url = "https://example.com/avatar.jpg"
    user.is_active = True
    user.sso_provider = "google"
    user.sso_id = "auth_123"
    user.created_at = "2024-01-01T00:00:00"
    return user


class TestAuthIntegration:

    @patch('src.api.routers.state_service')
    @patch('src.api.routers.google_oauth')
    def test_google_auth_cookie_settings(self, mock_google_oauth, mock_state_service, client):
        mock_state_service.generate_state.return_value = "test_state"
        mock_google_oauth.get_authorization_url.return_value = "https://accounts.google.com/o/oauth2/auth"

        response = client.get("/auth/google", allow_redirects=False)

        cookie = response.cookies.get("oauth_state")
        assert cookie is not None

        cookie_attrs = response.headers.get("set-cookie", "")
        assert "httponly" in cookie_attrs.lower()
        assert "samesite=lax" in cookie_attrs.lower()

    def test_token_verify_with_invalid_json(self, client):
        response = client.post("/auth/token/verify", data="invalid json")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_token_verify_missing_token_field(self, client):
        response = client.post("/auth/token/verify", json={"not_token": "value"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_auth_routes_exist(self, client):
        routes = [route.path for route in app.routes]

        assert "/auth/google" in routes
        assert "/auth/google/callback" in routes
        assert "/auth/token/verify" in routes

    def test_google_callback_without_cookie(self, client):
        response = client.get(
            "/auth/google/callback",
            params={"code": "test_code", "state": "valid_state"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Invalid state parameter"

    def test_google_callback_state_mismatch(self, client):
        client.cookies["oauth_state"] = "cookie_state"
        response = client.get(
            "/auth/google/callback",
            params={"code": "test_code", "state": "different_state"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Invalid state parameter"