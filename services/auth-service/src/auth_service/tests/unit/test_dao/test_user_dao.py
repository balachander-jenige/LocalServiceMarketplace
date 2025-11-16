"""
UserDAO 单元测试
测试用户数据访问层逻辑
"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from auth_service.dao.user_dao import UserDAO
from auth_service.models.user import User


class TestUserDAOCreate:
    """Test UserDAO.create_user"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db_session):
        """TestCreate UserSuccess"""
        # Act
        user = await UserDAO.create_user(
            db=mock_db_session,
            username="testuser",
            email="test@test.com",
            password_hash="hashed_password",
            role_id=1,
        )

        # Assert
        assert user.username == "testuser"
        assert user.email == "test@test.com"
        assert user.password_hash == "hashed_password"
        assert user.role_id == 1
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, mock_db_session):
        """TestDuplicateEmail"""
        # Mock commitThrowIntegrityError
        mock_db_session.commit.side_effect = IntegrityError(None, None, None)

        # VerifyThrowHTTPException
        with pytest.raises(HTTPException) as exc_info:
            await UserDAO.create_user(
                db=mock_db_session,
                username="testuser",
                email="existing@test.com",
                password_hash="hashed",
                role_id=1,
            )

        assert exc_info.value.status_code == 400
        assert "已存在" in exc_info.value.detail
        mock_db_session.rollback.assert_awaited_once()


class TestUserDAOGetByEmail:
    """Test UserDAO.get_user_by_email"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, mock_db_session):
        """TestQueryUser(Exists)"""
        # Arrange
        mock_user = MagicMock()
        mock_user.email = "test@test.com"
        mock_user.id = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await UserDAO.get_user_by_email(mock_db_session, "test@test.com")

        # Assert
        assert user is not None
        assert user.email == "test@test.com"
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_db_session):
        """TestQueryUser(Does Not Exist)"""
        # MockReturnNone
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await UserDAO.get_user_by_email(mock_db_session, "notexist@test.com")

        # Assert
        assert user is None


class TestUserDAOGetById:
    """Test UserDAO.get_user_by_id"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_db_session):
        """TestByIDQueryUser(Exists)"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db_session.get.return_value = mock_user

        user = await UserDAO.get_user_by_id(mock_db_session, 1)

        assert user is not None
        assert user.id == 1
        mock_db_session.get.assert_awaited_once_with(User, 1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """TestByIDQueryUser(Does Not Exist)"""
        mock_db_session.get.return_value = None

        user = await UserDAO.get_user_by_id(mock_db_session, 999)

        assert user is None


class TestUserDAOUpdate:
    """Test UserDAO.update_user"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db_session):
        """TestUpdateUserSuccess"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "oldname"
        mock_db_session.get.return_value = mock_user

        # Act
        updated_user = await UserDAO.update_user(
            db=mock_db_session, user_id=1, username="newname", email="new@test.com"
        )

        # Assert
        assert updated_user is not None
        assert updated_user.username == "newname"
        assert updated_user.email == "new@test.com"
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_db_session):
        """TestUpdateDoes Not Exist的User"""
        mock_db_session.get.return_value = None

        result = await UserDAO.update_user(db=mock_db_session, user_id=999, username="newname")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_with_role_id(self, mock_db_session):
        """TestUpdateUserRole"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role_id = 1
        mock_db_session.get.return_value = mock_user

        # Act
        updated_user = await UserDAO.update_user(db=mock_db_session, user_id=1, role_id=2)

        # Assert
        assert updated_user.role_id == 2
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_user_integrity_error(self, mock_db_session):
        """TestUpdateUserWhen发生DuplicateError"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db_session.get.return_value = mock_user
        mock_db_session.commit.side_effect = IntegrityError(None, None, None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await UserDAO.update_user(db=mock_db_session, user_id=1, username="duplicate")

        assert exc_info.value.status_code == 400
        mock_db_session.rollback.assert_awaited_once()


class TestUserDAOGetAllUsers:
    """Test UserDAO.get_all_users"""

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, mock_db_session):
        """TestGetAllUserSuccess"""
        # Arrange
        mock_user1 = MagicMock()
        mock_user1.id = 1
        mock_user1.username = "user1"

        mock_user2 = MagicMock()
        mock_user2.id = 2
        mock_user2.username = "user2"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_user1, mock_user2]
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        # Act
        users = await UserDAO.get_all_users(mock_db_session)

        # Assert
        assert len(users) == 2
        assert users[0].username == "user1"
        assert users[1].username == "user2"
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_users_with_role_filter(self, mock_db_session):
        """TestByRoleFilterGetUser"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role_id = 1

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_user]
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        # Act
        users = await UserDAO.get_all_users(mock_db_session, role_id=1)

        # Assert
        assert len(users) == 1
        assert users[0].role_id == 1
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_users_empty_list(self, mock_db_session):
        """TestGetEmptyUserList"""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        # Act
        users = await UserDAO.get_all_users(mock_db_session)

        # Assert
        assert len(users) == 0


class TestUserDAODeleteUser:
    """Test UserDAO.delete_user"""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, mock_db_session):
        """TestDelete UserSuccess"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db_session.get.return_value = mock_user

        # Act
        result = await UserDAO.delete_user(mock_db_session, user_id=1)

        # Assert
        assert result is True
        mock_db_session.execute.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_db_session):
        """TestDeleteDoes Not Exist的User"""
        # Arrange
        mock_db_session.get.return_value = None

        # Act
        result = await UserDAO.delete_user(mock_db_session, user_id=999)

        # Assert
        assert result is False
        mock_db_session.commit.assert_not_awaited()


class TestUserDAODeleteByUsername:
    """Test UserDAO.delete_user_by_username"""

    @pytest.mark.asyncio
    async def test_delete_user_by_username_success(self, mock_db_session):
        """TestByUserNameDelete UserSuccess"""
        # Arrange
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_user
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        # Act
        result = await UserDAO.delete_user_by_username(mock_db_session, username="testuser")

        # Assert
        assert result is True
        assert mock_db_session.execute.await_count == 2  # select + delete
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_user_by_username_not_found(self, mock_db_session):
        """TestDeleteDoes Not Exist的UserName"""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        # Act
        result = await UserDAO.delete_user_by_username(mock_db_session, username="nonexistent")

        # Assert
        assert result is False
        mock_db_session.commit.assert_not_awaited()
