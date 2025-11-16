"""
AdminUserService 单元测试
测试管理员用户管理功能
"""

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch

from auth_service.services.admin_user_service import AdminUserService


class TestAdminUserServiceGetAllUsers:
    """TestGet All Users List"""

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, mock_db_session):
        """TestGetAllUserSuccess"""
        # Arrange
        mock_user1 = MagicMock()
        mock_user1.id = 1
        mock_user1.username = "user1"
        mock_user1.email = "user1@test.com"
        mock_user1.role_id = 1

        mock_user2 = MagicMock()
        mock_user2.id = 2
        mock_user2.username = "user2"
        mock_user2.email = "user2@test.com"
        mock_user2.role_id = 2

        expected_users = [mock_user1, mock_user2]

        with patch("auth_service.services.admin_user_service.UserDAO.get_all_users") as mock_get_all:
            mock_get_all.return_value = expected_users

            # Act
            result = await AdminUserService.get_all_users(mock_db_session)

            # Assert
            assert result == expected_users
            assert len(result) == 2
            mock_get_all.assert_called_once_with(mock_db_session, None)

    @pytest.mark.asyncio
    async def test_get_all_users_with_role_filter(self, mock_db_session):
        """TestByRoleFilterUser"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role_id = 1
        expected_users = [mock_user]

        with patch("auth_service.services.admin_user_service.UserDAO.get_all_users") as mock_get_all:
            mock_get_all.return_value = expected_users

            # Act
            result = await AdminUserService.get_all_users(mock_db_session, role_id=1)

            # Assert
            assert result == expected_users
            mock_get_all.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_get_all_users_empty_list(self, mock_db_session):
        """TestGetEmptyUserList"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.get_all_users") as mock_get_all:
            mock_get_all.return_value = []

            # Act
            result = await AdminUserService.get_all_users(mock_db_session)

            # Assert
            assert result == []
            mock_get_all.assert_called_once()


class TestAdminUserServiceGetUserById:
    """TestGet User Details"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_db_session, mock_user_object):
        """TestSuccessGet User Details"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = mock_user_object

            # Act
            result = await AdminUserService.get_user_by_id(mock_db_session, user_id=1)

            # Assert
            assert result == mock_user_object
            mock_get.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """TestUserDoes Not ExistWhenThrow404Exception"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.get_user_by_id") as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminUserService.get_user_by_id(mock_db_session, user_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"


class TestAdminUserServiceUpdateUser:
    """TestUpdate User Information"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db_session):
        """TestSuccessUpdate User Information"""
        # Arrange
        mock_updated_user = MagicMock()
        mock_updated_user.id = 1
        mock_updated_user.username = "updated_user"
        mock_updated_user.email = "updated@test.com"
        mock_updated_user.role_id = 2

        with patch("auth_service.services.admin_user_service.UserDAO.update_user") as mock_update:
            mock_update.return_value = mock_updated_user

            # Act
            result = await AdminUserService.update_user(
                mock_db_session, user_id=1, username="updated_user", email="updated@test.com"
            )

            # Assert
            assert result == mock_updated_user
            mock_update.assert_called_once_with(
                mock_db_session, 1, username="updated_user", email="updated@test.com", role_id=None
            )

    @pytest.mark.asyncio
    async def test_update_user_with_role_id(self, mock_db_session):
        """TestUpdateUserRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 2
        mock_role.role_name = "provider"

        mock_updated_user = MagicMock()
        mock_updated_user.id = 1
        mock_updated_user.role_id = 2

        with patch("auth_service.services.admin_user_service.RoleDAO.get_role_by_id") as mock_get_role:
            mock_get_role.return_value = mock_role

            with patch("auth_service.services.admin_user_service.UserDAO.update_user") as mock_update:
                mock_update.return_value = mock_updated_user

                # Act
                result = await AdminUserService.update_user(mock_db_session, user_id=1, role_id=2)

                # Assert
                assert result == mock_updated_user
                mock_get_role.assert_called_once_with(mock_db_session, 2)
                mock_update.assert_called_once_with(mock_db_session, 1, username=None, email=None, role_id=2)

    @pytest.mark.asyncio
    async def test_update_user_invalid_role_id(self, mock_db_session):
        """Test使用No效的RoleIDUpdateUser"""
        # Arrange
        with patch("auth_service.services.admin_user_service.RoleDAO.get_role_by_id") as mock_get_role:
            mock_get_role.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminUserService.update_user(mock_db_session, user_id=1, role_id=999)

            assert exc_info.value.status_code == 400
            assert "Invalid role_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_db_session):
        """TestUpdateDoes Not Exist的User"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.update_user") as mock_update:
            mock_update.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminUserService.update_user(mock_db_session, user_id=999, username="new_name")

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_update_user_only_username(self, mock_db_session):
        """TestOnly UpdateUserName"""
        # Arrange
        mock_updated_user = MagicMock()
        mock_updated_user.username = "new_username"

        with patch("auth_service.services.admin_user_service.UserDAO.update_user") as mock_update:
            mock_update.return_value = mock_updated_user

            # Act
            result = await AdminUserService.update_user(mock_db_session, user_id=1, username="new_username")

            # Assert
            assert result.username == "new_username"
            mock_update.assert_called_once_with(mock_db_session, 1, username="new_username", email=None, role_id=None)

    @pytest.mark.asyncio
    async def test_update_user_only_email(self, mock_db_session):
        """TestOnly UpdateEmail"""
        # Arrange
        mock_updated_user = MagicMock()
        mock_updated_user.email = "new@test.com"

        with patch("auth_service.services.admin_user_service.UserDAO.update_user") as mock_update:
            mock_update.return_value = mock_updated_user

            # Act
            result = await AdminUserService.update_user(mock_db_session, user_id=1, email="new@test.com")

            # Assert
            assert result.email == "new@test.com"
            mock_update.assert_called_once_with(mock_db_session, 1, username=None, email="new@test.com", role_id=None)


class TestAdminUserServiceDeleteUser:
    """TestDelete User"""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, mock_db_session):
        """TestSuccessDelete User"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.delete_user") as mock_delete:
            mock_delete.return_value = True

            # Act
            result = await AdminUserService.delete_user(mock_db_session, user_id=1)

            # Assert
            assert result is True
            mock_delete.assert_called_once_with(mock_db_session, 1)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_db_session):
        """TestDeleteDoes Not Exist的User"""
        # Arrange
        with patch("auth_service.services.admin_user_service.UserDAO.delete_user") as mock_delete:
            mock_delete.return_value = False

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminUserService.delete_user(mock_db_session, user_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"
