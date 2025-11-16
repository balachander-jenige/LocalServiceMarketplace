"""
AuthService 单元测试
测试用户注册和登录核心业务逻辑
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from auth_service.core.security import hash_password
from auth_service.services.auth_service import AuthService


class TestAuthServiceRegister:
    """Test AuthService.register Method"""

    @pytest.mark.asyncio
    async def test_register_success(self, mock_db_session, mocker):
        """Test正常Registration流程"""
        # Arrange: PrepareMockObject
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@test.com"
        mock_user.role_id = 1

        # Mock UserDAO.create_user
        mock_create_user = mocker.patch(
            "auth_service.services.auth_service.UserDAO.create_user", return_value=mock_user
        )

        # Mock EventPublisher
        mock_publish = mocker.patch("auth_service.services.auth_service.EventPublisher.publish_user_registered")

        # Act: ExecuteRegistration
        result = await AuthService.register(
            db=mock_db_session, username="testuser", email="test@test.com", password="Test123!", role_id=1
        )

        # Assert: VerifyResult
        assert result.id == 1
        assert result.username == "testuser"
        assert result.email == "test@test.com"

        # VerifyUserDAOBe Called
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args
        # Verify With Positional Arguments
        assert call_args[0][1] == "testuser"  # username
        assert call_args[0][2] == "test@test.com"  # email
        assert call_args[0][4] == 1  # role_id
        # Verify密码Be Hashed
        assert call_args[0][3] != "Test123!"
        assert call_args[0][3].startswith("$2b$")

        # VerifyEventPublishBe Called
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_customer_role(self, mock_db_session, mocker):
        """TestRegistrationCustomerRole"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "customer"
        mock_user.email = "customer@test.com"
        mock_user.role_id = 1

        mocker.patch("auth_service.services.auth_service.UserDAO.create_user", return_value=mock_user)
        mocker.patch("auth_service.services.auth_service.EventPublisher.publish_user_registered")

        result = await AuthService.register(
            db=mock_db_session, username="customer", email="customer@test.com", password="Test123!", role_id=1
        )

        assert result.role_id == 1

    @pytest.mark.asyncio
    async def test_register_provider_role(self, mock_db_session, mocker):
        """TestRegistrationProviderRole"""
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user.username = "provider"
        mock_user.email = "provider@test.com"
        mock_user.role_id = 2

        mocker.patch("auth_service.services.auth_service.UserDAO.create_user", return_value=mock_user)
        mocker.patch("auth_service.services.auth_service.EventPublisher.publish_user_registered")

        result = await AuthService.register(
            db=mock_db_session, username="provider", email="provider@test.com", password="Test123!", role_id=2
        )

        assert result.role_id == 2

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, mock_db_session, mocker):
        """TestDuplicateEmailRegistration"""
        # Mock UserDAOThrowHTTPException
        mocker.patch(
            "auth_service.services.auth_service.UserDAO.create_user",
            side_effect=HTTPException(status_code=400, detail="用户名或邮箱已存在"),
        )

        # VerifyThrowException
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.register(
                db=mock_db_session, username="testuser", email="existing@test.com", password="Test123!", role_id=1
            )

        assert exc_info.value.status_code == 400
        assert "已存在" in exc_info.value.detail


class TestAuthServiceLogin:
    """Test AuthService.login Method"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db_session, mocker):
        """Test正常Login"""
        # Arrange: CreateMockUser
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role_id = 1
        mock_user.password_hash = hash_password("Test123!")

        # Mock UserDAO.get_user_by_email
        mocker.patch("auth_service.services.auth_service.UserDAO.get_user_by_email", return_value=mock_user)

        # Act: ExecuteLogin
        token = await AuthService.login(db=mock_db_session, email="test@test.com", password="Test123!")

        # Assert: Verifytoken
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # VerifytokenCan以解码
        from jose import jwt

        from auth_service.core.config import settings

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == 1
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_db_session, mocker):
        """TestError密码"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.password_hash = hash_password("CorrectPassword")

        mocker.patch("auth_service.services.auth_service.UserDAO.get_user_by_email", return_value=mock_user)

        # VerifyThrow401Exception
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.login(db=mock_db_session, email="test@test.com", password="WrongPassword")

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_db_session, mocker):
        """TestUserDoes Not Exist"""
        # MockReturnNone
        mocker.patch("auth_service.services.auth_service.UserDAO.get_user_by_email", return_value=None)

        # VerifyThrow401Exception
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.login(db=mock_db_session, email="notexist@test.com", password="Test123!")

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_token_contains_user_id_and_role(self, mock_db_session, mocker):
        """TesttokenContainsCorrect的user_idAndrole"""
        mock_user = MagicMock()
        mock_user.id = 99
        mock_user.role_id = 2  # Provider
        mock_user.password_hash = hash_password("Test123!")

        mocker.patch("auth_service.services.auth_service.UserDAO.get_user_by_email", return_value=mock_user)

        token = await AuthService.login(db=mock_db_session, email="provider@test.com", password="Test123!")

        # 解码tokenVerify内容
        from jose import jwt

        from auth_service.core.config import settings

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "99"
        assert payload["role"] == 2
