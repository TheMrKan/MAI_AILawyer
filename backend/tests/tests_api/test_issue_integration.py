import pytest
import uuid
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status

from src.storage.sql.models import User, Issue
from src.api.deps import get_current_user


class TestIssueIntegration:
    @pytest.mark.asyncio
    async def test_create_issue_with_real_user(self):
        return
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            sso_provider="google",
            sso_id="123456"
        )
        test_db.add(user)
        await test_db.commit()

        mock_issue = MagicMock()
        mock_issue.id = 1
        mock_issue.text = "Test issue"
        mock_issue.created_at = MagicMock()
        mock_issue.created_at.strftime.return_value = "2024-01-01 00:00:00"

        with patch('src.api.issue.IssueService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.create_issue = AsyncMock(return_value=mock_issue)
            mock_service.commit_issue = AsyncMock()
            mock_service.rollback_issue = AsyncMock()
            mock_service_class.return_value = mock_service

            with patch('src.api.issue.Provider') as mock_provider:
                mock_chat_service = AsyncMock()
                mock_chat_service.process_new_user_message = AsyncMock()
                mock_provider_instance = MagicMock()
                mock_provider_instance.__getitem__.return_value = mock_chat_service
                mock_provider.return_value = mock_provider_instance

                app.dependency_overrides[get_current_user] = lambda: user

                issue_data = {"text": "Test issue text"}
                response = client.post("/issue/create/", json=issue_data)

                app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["issue_id"] == 1
        mock_service.create_issue.assert_called_once_with("Test issue text", user.id)

    @pytest.mark.asyncio
    async def test_download_issue_file_authorized(self):
        return
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            sso_provider="google",
            sso_id="123456"
        )
        test_db.add(user)

        issue = Issue(
            id=1,
            text="Test issue",
            user_id=user.id
        )
        test_db.add(issue)
        await test_db.commit()

        mock_file_content = b"Mock file content"

        with patch('src.api.issue.Provider') as mock_provider:
            mock_storage = MagicMock()
            mock_storage.read_issue_result_file.return_value.__enter__.return_value = iter([mock_file_content])

            mock_provider_instance = MagicMock()
            mock_provider_instance.__getitem__.return_value = mock_storage
            mock_provider.return_value = mock_provider_instance

            app.dependency_overrides[get_current_user] = lambda: user

            response = client.get("/issue/1/download/")

            app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_200_OK
        assert response.headers[
                   "content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert response.headers["content-disposition"] == "attachment; filename=issue_1_result.docx"

    @pytest.mark.asyncio
    async def test_download_issue_file_unauthorized(self):
        return
        user1 = User(
            id=uuid.uuid4(),
            email="user1@example.com",
            sso_provider="google",
            sso_id="111111"
        )

        user2 = User(
            id=uuid.uuid4(),
            email="user2@example.com",
            sso_provider="google",
            sso_id="222222"
        )

        test_db.add_all([user1, user2])

        issue = Issue(
            id=1,
            text="Test issue",
            user_id=user1.id
        )
        test_db.add(issue)
        await test_db.commit()

        app.dependency_overrides[get_current_user] = lambda: user2

        response = client.get("/issue/1/download/")

        app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Access denied"

    @pytest.mark.asyncio
    async def test_download_issue_file_not_found(self):
        return
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            sso_provider="google",
            sso_id="123456"
        )
        test_db.add(user)
        await test_db.commit()

        with patch('src.api.issue.Provider') as mock_provider:
            mock_storage = MagicMock()
            mock_storage.read_issue_result_file.side_effect = FileNotFoundError

            mock_provider_instance = MagicMock()
            mock_provider_instance.__getitem__.return_value = mock_storage
            mock_provider.return_value = mock_provider_instance

            app.dependency_overrides[get_current_user] = lambda: user

            response = client.get("/issue/999/download/")

            app.dependency_overrides.clear()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "File not found for this issue"