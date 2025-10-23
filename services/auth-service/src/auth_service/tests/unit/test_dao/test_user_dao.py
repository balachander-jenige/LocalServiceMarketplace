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
    """测试 UserDAO.create_user"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db_session):
        """测试创建用户成功"""
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
        """测试重复邮箱"""
        # Mock commit抛出IntegrityError
        mock_db_session.commit.side_effect = IntegrityError(None, None, None)

        # 验证抛出HTTPException
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
    """测试 UserDAO.get_user_by_email"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, mock_db_session):
        """测试查询用户(存在)"""
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
        """测试查询用户(不存在)"""
        # Mock返回None
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        user = await UserDAO.get_user_by_email(mock_db_session, "notexist@test.com")

        # Assert
        assert user is None


class TestUserDAOGetById:
    """测试 UserDAO.get_user_by_id"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_db_session):
        """测试根据ID查询用户(存在)"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db_session.get.return_value = mock_user

        user = await UserDAO.get_user_by_id(mock_db_session, 1)

        assert user is not None
        assert user.id == 1
        mock_db_session.get.assert_awaited_once_with(User, 1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """测试根据ID查询用户(不存在)"""
        mock_db_session.get.return_value = None

        user = await UserDAO.get_user_by_id(mock_db_session, 999)

        assert user is None


class TestUserDAOUpdate:
    """测试 UserDAO.update_user"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_db_session):
        """测试更新用户成功"""
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
        """测试更新不存在的用户"""
        mock_db_session.get.return_value = None

        result = await UserDAO.update_user(db=mock_db_session, user_id=999, username="newname")

        assert result is None
