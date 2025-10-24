"""
UserService 单元测试
测试用户服务功能
"""

import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from auth_service.services.user_service import UserService


class TestUserServiceGetUserById:
    """测试获取用户信息"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_db_session, mock_user_object):
        """测试成功获取用户信息"""
        # Arrange
        with patch("auth_service.services.user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = mock_user_object

            # Act
            result = await UserService.get_user_by_id(mock_db_session, user_id=1)

            # Assert
            assert result == mock_user_object
            assert result.id == 1
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            mock_get.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """测试用户不存在时抛出404异常"""
        # Arrange
        with patch("auth_service.services.user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await UserService.get_user_by_id(mock_db_session, user_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"
            mock_get.assert_called_once_with(mock_db_session, 999)

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_different_users(self, mock_db_session):
        """测试获取不同角色的用户"""
        # Arrange - Customer
        mock_customer = MagicMock()
        mock_customer.id = 1
        mock_customer.username = "customer1"
        mock_customer.role_id = 1

        with patch("auth_service.services.user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = mock_customer

            # Act
            result = await UserService.get_user_by_id(mock_db_session, user_id=1)

            # Assert
            assert result.role_id == 1
            assert result.username == "customer1"

        # Arrange - Provider
        mock_provider = MagicMock()
        mock_provider.id = 2
        mock_provider.username = "provider1"
        mock_provider.role_id = 2

        with patch("auth_service.services.user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = mock_provider

            # Act
            result = await UserService.get_user_by_id(mock_db_session, user_id=2)

            # Assert
            assert result.role_id == 2
            assert result.username == "provider1"
