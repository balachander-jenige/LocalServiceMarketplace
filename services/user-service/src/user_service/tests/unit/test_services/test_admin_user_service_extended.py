"""
AdminUserService 扩展测试 - 补充 update_user 和 delete_user 测试
覆盖原测试未覆盖的代码路径
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException

from user_service.services.admin_user_service import AdminUserService
from user_service.dto.admin_dto import UpdateUserRequest
from user_service.models.customer_profile import CustomerProfile
from user_service.models.provider_profile import ProviderProfile
from datetime import datetime


class TestAdminUserServiceUpdateUser:
    """测试 update_user 方法"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_update_customer_username_and_location(self, service, mocker):
        """测试更新 Customer 用户名和位置"""
        # Mock HTTP 响应
        mock_response_put = MagicMock()
        mock_response_put.status_code = 200
        mock_response_put.json.return_value = {"id": 1, "username": "new_customer"}

        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {
            "id": 1,
            "username": "new_customer",
            "email": "customer@test.com",
            "role_id": 1,
            "created_at": "2024-01-01T00:00:00",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.put.return_value = mock_response_put
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Mock DAO
        mock_customer = CustomerProfile(
            user_id=1,
            location="NORTH",
            address="123 Main St",
            budget_preference=1000.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=mock_customer)
        mocker.patch.object(service.customer_dao, "update", return_value=mock_customer)

        # Mock get_user_detail 返回值
        mock_detail = {
            "user_id": 1,
            "username": "new_customer",
            "email": "customer@test.com",
            "role_id": 1,
            "role_name": "customer",
            "profile": mock_customer.model_dump(mode="json"),
        }
        mocker.patch.object(service, "get_user_detail", return_value=mock_detail)

        # 执行测试
        update_data = UpdateUserRequest(username="new_customer", location="SOUTH")
        result = await service.update_user(user_id=1, update_data=update_data)

        # 验证结果
        assert result["username"] == "new_customer"
        assert result["role_id"] == 1

        # 验证 Auth Service 调用
        mock_client.put.assert_called_once()
        put_call_args = mock_client.put.call_args
        assert "username" in put_call_args[1]["json"]

        # 验证 DAO 更新调用
        service.customer_dao.update.assert_called_once_with(user_id=1, update_data={"location": "SOUTH"})

    @pytest.mark.asyncio
    async def test_update_provider_skills_and_hourly_rate(self, service, mocker):
        """测试更新 Provider 技能和时薪"""
        # Mock HTTP 响应
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {
            "id": 2,
            "username": "provider_user",
            "email": "provider@test.com",
            "role_id": 2,
            "created_at": "2024-01-01T00:00:00",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Mock DAO
        mock_provider = ProviderProfile(
            user_id=2,
            skills=["Python", "FastAPI"],
            experience_years=5,
            hourly_rate=50.0,
            availability="FULL_TIME",
            portfolio=[],
            rating=4.5,
            total_reviews=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=mock_provider)
        mocker.patch.object(service.provider_dao, "update", return_value=mock_provider)

        # Mock get_user_detail
        mock_detail = {
            "user_id": 2,
            "username": "provider_user",
            "email": "provider@test.com",
            "role_id": 2,
            "role_name": "provider",
            "profile": mock_provider.model_dump(mode="json"),
        }
        mocker.patch.object(service, "get_user_detail", return_value=mock_detail)

        # 执行测试
        update_data = UpdateUserRequest(skills=["Python", "Django", "React"], hourly_rate=80.0)
        result = await service.update_user(user_id=2, update_data=update_data)

        # 验证结果
        assert result["role_id"] == 2

        # 验证 DAO 更新调用
        service.provider_dao.update.assert_called_once_with(
            user_id=2, update_data={"skills": ["Python", "Django", "React"], "hourly_rate": 80.0}
        )

    @pytest.mark.asyncio
    async def test_update_customer_profile_not_exists(self, service, mocker):
        """测试更新 Customer,但 Profile 不存在"""
        # Mock HTTP 响应
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {
            "id": 3,
            "username": "customer_no_profile",
            "email": "no_profile@test.com",
            "role_id": 1,
            "created_at": "2024-01-01T00:00:00",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Mock DAO - Profile 不存在
        mock_get = mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mock_update = mocker.patch.object(service.customer_dao, "update", return_value=None)

        # Mock get_user_detail
        mock_detail = {
            "user_id": 3,
            "username": "customer_no_profile",
            "email": "no_profile@test.com",
            "role_id": 1,
            "role_name": "customer",
            "profile": None,
        }
        mocker.patch.object(service, "get_user_detail", return_value=mock_detail)

        # 执行测试 - 即使 Profile 不存在,update_user 也应该成功(只更新 Auth 部分)
        update_data = UpdateUserRequest(location="EAST")
        result = await service.update_user(user_id=3, update_data=update_data)

        # 验证结果
        assert result["user_id"] == 3

        # 验证 DAO update 未被调用(因为 Profile 不存在)
        mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_auth_service_error(self, service, mocker):
        """测试更新用户时 Auth Service 返回错误"""
        # Mock HTTP PUT 返回错误
        mock_response_put = MagicMock()
        mock_response_put.status_code = 400
        mock_response_put.json.return_value = {"detail": "Invalid username"}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.put.return_value = mock_response_put

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        update_data = UpdateUserRequest(username="invalid@@@")

        with pytest.raises(HTTPException) as exc_info:
            await service.update_user(user_id=1, update_data=update_data)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, service, mocker):
        """测试更新不存在的用户"""
        # Mock HTTP PUT 成功(更新Auth部分)
        mock_response_put = MagicMock()
        mock_response_put.status_code = 200

        # Mock HTTP GET 返回 404
        mock_response_get = MagicMock()
        mock_response_get.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.put.return_value = mock_response_put
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        update_data = UpdateUserRequest(username="new_name")

        with pytest.raises(HTTPException) as exc_info:
            await service.update_user(user_id=999, update_data=update_data)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_update_provider_multiple_fields(self, service, mocker):
        """测试更新 Provider 多个字段"""
        # Mock HTTP 响应
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.json.return_value = {
            "id": 4,
            "username": "provider_multi",
            "email": "multi@test.com",
            "role_id": 2,
            "created_at": "2024-01-01T00:00:00",
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Mock DAO
        mock_provider = ProviderProfile(
            user_id=4,
            skills=["Java"],
            experience_years=3,
            hourly_rate=60.0,
            availability="PART_TIME",
            portfolio=["project1"],
            rating=4.0,
            total_reviews=5,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=mock_provider)
        mocker.patch.object(service.provider_dao, "update", return_value=mock_provider)

        # Mock get_user_detail
        mock_detail = {"user_id": 4, "role_id": 2}
        mocker.patch.object(service, "get_user_detail", return_value=mock_detail)

        # 执行测试 - 更新多个字段
        update_data = UpdateUserRequest(
            experience_years=10, availability="FULL_TIME", portfolio=["project1", "project2", "project3"]
        )
        result = await service.update_user(user_id=4, update_data=update_data)

        # 验证 DAO 调用包含所有字段
        service.provider_dao.update.assert_called_once()
        call_args = service.provider_dao.update.call_args
        assert call_args[1]["update_data"]["experience_years"] == 10
        assert call_args[1]["update_data"]["availability"] == "FULL_TIME"
        assert len(call_args[1]["update_data"]["portfolio"]) == 3


class TestAdminUserServiceDeleteUser:
    """测试 delete_user 方法"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_delete_customer_with_profile(self, service, mocker):
        """测试删除有 Profile 的 Customer"""
        # Mock DAO - Customer Profile 存在
        mock_customer = CustomerProfile(
            user_id=1,
            location="NORTH",
            address="123 Main St",
            budget_preference=1000.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=mock_customer)
        mocker.patch.object(service.customer_dao, "delete", return_value=True)

        # Provider Profile 不存在
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP 删除响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        result = await service.delete_user(user_id=1)

        # 验证结果
        assert result is True

        # 验证 Customer Profile 被删除
        service.customer_dao.delete.assert_called_once_with(1)

        # 验证 Auth Service 删除被调用
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_provider_with_profile(self, service, mocker):
        """测试删除有 Profile 的 Provider"""
        # Mock DAO - Provider Profile 存在
        mock_provider = ProviderProfile(
            user_id=2,
            skills=["Python"],
            experience_years=5,
            hourly_rate=50.0,
            availability="FULL_TIME",
            portfolio=[],
            rating=4.5,
            total_reviews=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=mock_provider)
        mocker.patch.object(service.provider_dao, "delete", return_value=True)

        # Customer Profile 不存在
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)

        # Mock HTTP 删除响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        result = await service.delete_user(user_id=2)

        # 验证结果
        assert result is True

        # 验证 Provider Profile 被删除
        service.provider_dao.delete.assert_called_once_with(2)

        # 验证 Auth Service 删除被调用
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_without_profile(self, service, mocker):
        """测试删除没有 Profile 的用户(Admin)"""
        # Mock DAO - 两种 Profile 都不存在
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)
        
        # Mock delete 方法(即使不会被调用,也要Mock)
        mock_customer_delete = mocker.patch.object(service.customer_dao, "delete")
        mock_provider_delete = mocker.patch.object(service.provider_dao, "delete")

        # Mock HTTP 删除响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        result = await service.delete_user(user_id=3)

        # 验证结果
        assert result is True

        # 验证 DAO delete 未被调用
        mock_customer_delete.assert_not_called()
        mock_provider_delete.assert_not_called()

        # 验证 Auth Service 删除仍被调用
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, service, mocker):
        """测试删除不存在的用户"""
        # Mock DAO - Profile 不存在
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP 返回 404
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_user(user_id=999)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_delete_user_auth_service_error(self, service, mocker):
        """测试删除用户时 Auth Service 返回错误"""
        # Mock DAO
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP 返回 500
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # 执行测试
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_user(user_id=1)

        assert exc_info.value.status_code == 500


class TestAdminUserServiceHelperMethods:
    """测试辅助方法 _check_profile_exists 和 _get_role_name"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_check_profile_exists_customer_true(self, service, mocker):
        """测试 Customer Profile 存在"""
        mock_customer = CustomerProfile(
            user_id=1,
            location="NORTH",
            address="123 Main St",
            budget_preference=1000.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=mock_customer)

        result = await service._check_profile_exists(user_id=1, role_id=1)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_profile_exists_customer_false(self, service, mocker):
        """测试 Customer Profile 不存在"""
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)

        result = await service._check_profile_exists(user_id=1, role_id=1)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_provider_true(self, service, mocker):
        """测试 Provider Profile 存在"""
        mock_provider = ProviderProfile(
            user_id=2,
            skills=["Python"],
            experience_years=5,
            hourly_rate=50.0,
            availability="FULL_TIME",
            portfolio=[],
            rating=4.5,
            total_reviews=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=mock_provider)

        result = await service._check_profile_exists(user_id=2, role_id=2)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_profile_exists_provider_false(self, service, mocker):
        """测试 Provider Profile 不存在"""
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        result = await service._check_profile_exists(user_id=2, role_id=2)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_admin_role(self, service):
        """测试 Admin 角色(无 Profile)"""
        result = await service._check_profile_exists(user_id=3, role_id=3)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_unknown_role(self, service):
        """测试未知角色"""
        result = await service._check_profile_exists(user_id=4, role_id=99)
        assert result is False

    def test_get_role_name_customer(self, service):
        """测试获取 Customer 角色名"""
        assert service._get_role_name(1) == "customer"

    def test_get_role_name_provider(self, service):
        """测试获取 Provider 角色名"""
        assert service._get_role_name(2) == "provider"

    def test_get_role_name_admin(self, service):
        """测试获取 Admin 角色名"""
        assert service._get_role_name(3) == "admin"

    def test_get_role_name_unknown(self, service):
        """测试未知角色名"""
        assert service._get_role_name(99) == "unknown"
