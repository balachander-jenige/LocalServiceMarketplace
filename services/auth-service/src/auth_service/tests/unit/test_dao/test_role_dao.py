"""
RoleDAO 单元测试
测试角色数据访问对象
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from auth_service.dao.role_dao import RoleDAO


class TestRoleDAOGetRoleById:
    """TestByIDGetRole"""

    @pytest.mark.asyncio
    async def test_get_role_by_id_success(self, mock_db_session):
        """TestSuccessGetRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 1
        mock_role.role_name = "customer"
        mock_role.description = "Customer role"

        mock_db_session.get = AsyncMock(return_value=mock_role)

        # Act
        result = await RoleDAO.get_role_by_id(mock_db_session, role_id=1)

        # Assert
        assert result == mock_role
        assert result.id == 1
        assert result.role_name == "customer"
        mock_db_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_id_not_found(self, mock_db_session):
        """TestRoleDoes Not ExistWhenReturnNone"""
        # Arrange
        mock_db_session.get = AsyncMock(return_value=None)

        # Act
        result = await RoleDAO.get_role_by_id(mock_db_session, role_id=999)

        # Assert
        assert result is None
        mock_db_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_id_provider(self, mock_db_session):
        """TestGetproviderRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 2
        mock_role.role_name = "provider"

        mock_db_session.get = AsyncMock(return_value=mock_role)

        # Act
        result = await RoleDAO.get_role_by_id(mock_db_session, role_id=2)

        # Assert
        assert result.role_name == "provider"

    @pytest.mark.asyncio
    async def test_get_role_by_id_admin(self, mock_db_session):
        """TestGetadminRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 3
        mock_role.role_name = "admin"

        mock_db_session.get = AsyncMock(return_value=mock_role)

        # Act
        result = await RoleDAO.get_role_by_id(mock_db_session, role_id=3)

        # Assert
        assert result.role_name == "admin"


class TestRoleDAOGetRoleByName:
    """TestByName称GetRole"""

    @pytest.mark.asyncio
    async def test_get_role_by_name_success(self, mock_db_session):
        """TestSuccessByName称GetRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 1
        mock_role.role_name = "customer"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first = MagicMock(return_value=mock_role)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await RoleDAO.get_role_by_name(mock_db_session, role_name="customer")

        # Assert
        assert result == mock_role
        assert result.role_name == "customer"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_name_not_found(self, mock_db_session):
        """TestRoleName称Does Not ExistWhenReturnNone"""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first = MagicMock(return_value=None)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await RoleDAO.get_role_by_name(mock_db_session, role_name="nonexistent")

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_by_name_provider(self, mock_db_session):
        """TestByName称GetproviderRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 2
        mock_role.role_name = "provider"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first = MagicMock(return_value=mock_role)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await RoleDAO.get_role_by_name(mock_db_session, role_name="provider")

        # Assert
        assert result.role_name == "provider"

    @pytest.mark.asyncio
    async def test_get_role_by_name_admin(self, mock_db_session):
        """TestByName称GetadminRole"""
        # Arrange
        mock_role = MagicMock()
        mock_role.id = 3
        mock_role.role_name = "admin"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first = MagicMock(return_value=mock_role)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await RoleDAO.get_role_by_name(mock_db_session, role_name="admin")

        # Assert
        assert result.role_name == "admin"

    @pytest.mark.asyncio
    async def test_get_role_by_name_case_sensitive(self, mock_db_session):
        """TestRoleName称Case Sensitive"""
        # Arrange
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first = MagicMock(return_value=None)
        mock_result.scalars = MagicMock(return_value=mock_scalars)

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await RoleDAO.get_role_by_name(mock_db_session, role_name="CUSTOMER")

        # Assert
        assert result is None  # BecauseShould Be "customer" Not "CUSTOMER"
