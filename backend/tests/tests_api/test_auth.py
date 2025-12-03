import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
import json
import urllib.parse

from src.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_oauth_user_data():
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "avatar_url": "https://example.com/avatar.jpg",
        "sso_provider": "google",
        "sso_id": "123456789"
    }


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "123e4567-e89b-12d3-a456-426614174000"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.avatar_url = "https://example.com/avatar.jpg"
    return user


@pytest.fixture
def mock_token_response():
    token = MagicMock()
    token.access_token = "test_token"
    token.token_type = "bearer"
    token.expires_in = 3600
    return token


class TestAuthRoutes:

    @patch('src.api.routers.state_service')
    @patch('src.api.routers.google_oauth')
    def test_google_auth(self, mock_google_oauth, mock_state_service, client):
        mock_state_service.generate_state.return_value = "test_state"
        mock_google_oauth.get_authorization_url.return_value = "https://accounts.google.com/o/oauth2/auth"

        response = client.get("/auth/google", allow_redirects=False)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "oauth_state" in response.cookies
        assert response.headers["location"] == "https://accounts.google.com/o/oauth2/auth"
        mock_state_service.generate_state.assert_called_once()
        mock_google_oauth.get_authorization_url.assert_called_once_with("test_state")

    @patch('src.api.routers.google_oauth')
    @patch('src.api.routers.auth_service')
    @patch('src.api.routers.UserRepository')
    def test_google_callback_success_with_frontend(self, mock_user_repo, mock_auth_service,
                                                   mock_google_oauth, client, mock_oauth_user_data, mock_user,
                                                   mock_token_response):
        mock_google_oauth.get_user_info = AsyncMock(return_value=mock_oauth_user_data)

        mock_user_repo_instance = AsyncMock()
        mock_user_repo_instance.get_or_create = AsyncMock(return_value=mock_user)
        mock_user_repo.return_value = mock_user_repo_instance

        mock_auth_service.create_token_response.return_value = mock_token_response

        with patch('src.api.routers.settings.FRONTEND_URL', 'http://localhost:3000'):
            with patch('src.api.routers.state_service.validate_state', return_value=True):
                client.cookies["oauth_state"] = "valid_state"
                response = client.get(
                    "/auth/google/callback",
                    params={"code": "test_code", "state": "valid_state"}
                )

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "oauth_state" not in response.cookies

        redirect_url = response.headers["location"]
        assert redirect_url.startswith("http://localhost:3000/auth/callback?data=")

        data_param = redirect_url.split("data=")[1]
        decoded_data = urllib.parse.unquote(data_param)
        response_data = json.loads(decoded_data)

        assert response_data["access_token"] == "test_token"
        assert response_data["user"]["email"] == "test@example.com"

    @patch('src.api.routers.google_oauth')
    @patch('src.api.routers.UserRepository')
    @patch('src.api.routers.auth_service')
    def test_google_callback_success_no_frontend(self, mock_auth_service, mock_user_repo,
                                                 mock_google_oauth, client, mock_oauth_user_data, mock_user,
                                                 mock_token_response):
        mock_google_oauth.get_user_info = AsyncMock(return_value=mock_oauth_user_data)

        mock_user_repo_instance = AsyncMock()
        mock_user_repo_instance.get_or_create = AsyncMock(return_value=mock_user)
        mock_user_repo.return_value = mock_user_repo_instance

        mock_auth_service.create_token_response.return_value = mock_token_response

        with patch('src.api.routers.settings.FRONTEND_URL', None):
            with patch('src.api.routers.state_service.validate_state', return_value=True):
                client.cookies["oauth_state"] = "valid_state"
                response = client.get(
                    "/auth/google/callback",
                    params={"code": "test_code", "state": "valid_state"}
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["access_token"] == "test_token"
        assert response_data["token_type"] == "bearer"
        assert response_data["expires_in"] == 3600

    def test_google_callback_missing_parameters(self, client):
        response = client.get("/auth/google/callback")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Missing code or state parameters"

    def test_google_callback_invalid_state(self, client):
        client.cookies["oauth_state"] = "cookie_state"

        with patch('src.api.routers.state_service.validate_state', return_value=False):
            response = client.get(
                "/auth/google/callback",
                params={"code": "test_code", "state": "invalid_state"}
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Invalid state parameter"

    @pytest.mark.parametrize("error_param", ["access_denied", "invalid_request", "unauthorized_client"])
    def test_google_callback_oauth_error(self, client, error_param):
        response = client.get(
            "/auth/google/callback",
            params={"error": error_param}
        )

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    @patch('src.api.routers.auth_service')
    def test_verify_token_valid(self, mock_auth_service, client):
        mock_token_data = MagicMock()
        mock_token_data.user_id = "test_user_id"
        mock_token_data.email = "test@example.com"
        mock_auth_service.verify_token.return_value = mock_token_data

        response = client.post("/auth/token/verify", json={"token": "valid_token"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] == True
        assert response.json()["user_id"] == "test_user_id"

    @patch('src.api.routers.auth_service')
    def test_verify_token_invalid(self, mock_auth_service, client):
        mock_auth_service.verify_token.return_value = None

        response = client.post("/auth/token/verify", json={"token": "invalid_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token"

    @patch('src.api.routers.auth_service')
    @pytest.mark.parametrize("token_value", ["", None, " "])
    def test_verify_token_empty_or_none(self, mock_auth_service, client, token_value):
        response = client.post("/auth/token/verify", json={"token": token_value})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('src.api.routers.google_oauth')
    @patch('src.api.routers.auth_service')
    @patch('src.api.routers.UserRepository')
    def test_google_callback_user_repo_exception(self, mock_user_repo, mock_auth_service,
                                                 mock_google_oauth, client, mock_oauth_user_data):
        mock_google_oauth.get_user_info = AsyncMock(return_value=mock_oauth_user_data)

        mock_user_repo_instance = AsyncMock()
        mock_user_repo_instance.get_or_create = AsyncMock(side_effect=Exception("DB Error"))
        mock_user_repo.return_value = mock_user_repo_instance

        with patch('src.api.routers.state_service.validate_state', return_value=True):
            client.cookies["oauth_state"] = "valid_state"
            response = client.get(
                "/auth/google/callback",
                params={"code": "test_code", "state": "valid_state"}
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Authentication failed"

    @patch('src.api.routers.google_oauth')
    def test_google_callback_oauth_exception(self, mock_google_oauth, client):
        mock_google_oauth.get_user_info = AsyncMock(side_effect=ValueError("Invalid OAuth token"))

        with patch('src.api.routers.state_service.validate_state', return_value=True):
            client.cookies["oauth_state"] = "valid_state"
            response = client.get(
                "/auth/google/callback",
                params={"code": "test_code", "state": "valid_state"}
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid OAuth token" in response.json()["detail"]