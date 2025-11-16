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
    """Test update_user Method"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_update_customer_username_and_location(self, service, mocker):
        """TestUpdate Customer UserNameAndLocation"""
        # Mock HTTP Response
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

        # Mock get_user_detail Return Value
        mock_detail = {
            "user_id": 1,
            "username": "new_customer",
            "email": "customer@test.com",
            "role_id": 1,
            "role_name": "customer",
            "profile": mock_customer.model_dump(mode="json"),
        }
        mocker.patch.object(service, "get_user_detail", return_value=mock_detail)

        # ExecuteTest
        update_data = UpdateUserRequest(username="new_customer", location="SOUTH")
        result = await service.update_user(user_id=1, update_data=update_data)

        # VerifyResult
        assert result["username"] == "new_customer"
        assert result["role_id"] == 1

        # Verify Auth Service Call
        mock_client.put.assert_called_once()
        put_call_args = mock_client.put.call_args
        assert "username" in put_call_args[1]["json"]

        # Verify DAO UpdateCall
        service.customer_dao.update.assert_called_once_with(user_id=1, update_data={"location": "SOUTH"})

    @pytest.mark.asyncio
    async def test_update_provider_skills_and_hourly_rate(self, service, mocker):
        """TestUpdate Provider SkillsAndHourly Rate"""
        # Mock HTTP Response
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

        # ExecuteTest
        update_data = UpdateUserRequest(skills=["Python", "Django", "React"], hourly_rate=80.0)
        result = await service.update_user(user_id=2, update_data=update_data)

        # VerifyResult
        assert result["role_id"] == 2

        # Verify DAO UpdateCall
        service.provider_dao.update.assert_called_once_with(
            user_id=2, update_data={"skills": ["Python", "Django", "React"], "hourly_rate": 80.0}
        )

    @pytest.mark.asyncio
    async def test_update_customer_profile_not_exists(self, service, mocker):
        """TestUpdate Customer,But Profile Does Not Exist"""
        # Mock HTTP Response
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

        # Mock DAO - Profile Does Not Exist
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

        # ExecuteTest - Even If Profile Does Not Exist,update_user Should AlsoSuccess(Only Update Auth Part)
        update_data = UpdateUserRequest(location="EAST")
        result = await service.update_user(user_id=3, update_data=update_data)

        # VerifyResult
        assert result["user_id"] == 3

        # Verify DAO update Not Called(Because Profile Does Not Exist)
        mock_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_auth_service_error(self, service, mocker):
        """TestUpdateUserWhen Auth Service ReturnError"""
        # Mock HTTP PUT ReturnError
        mock_response_put = MagicMock()
        mock_response_put.status_code = 400
        mock_response_put.json.return_value = {"detail": "Invalid username"}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.put.return_value = mock_response_put

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        update_data = UpdateUserRequest(username="invalid@@@")

        with pytest.raises(HTTPException) as exc_info:
            await service.update_user(user_id=1, update_data=update_data)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, service, mocker):
        """TestUpdateDoes Not Exist的User"""
        # Mock HTTP PUT Success(UpdateAuthPart)
        mock_response_put = MagicMock()
        mock_response_put.status_code = 200

        # Mock HTTP GET Return 404
        mock_response_get = MagicMock()
        mock_response_get.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.put.return_value = mock_response_put
        mock_client.get.return_value = mock_response_get

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        update_data = UpdateUserRequest(username="new_name")

        with pytest.raises(HTTPException) as exc_info:
            await service.update_user(user_id=999, update_data=update_data)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_update_provider_multiple_fields(self, service, mocker):
        """TestUpdate Provider MultipleFields"""
        # Mock HTTP Response
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

        # ExecuteTest - UpdateMultipleFields
        update_data = UpdateUserRequest(
            experience_years=10, availability="FULL_TIME", portfolio=["project1", "project2", "project3"]
        )
        result = await service.update_user(user_id=4, update_data=update_data)

        # Verify DAO CallContainsAllFields
        service.provider_dao.update.assert_called_once()
        call_args = service.provider_dao.update.call_args
        assert call_args[1]["update_data"]["experience_years"] == 10
        assert call_args[1]["update_data"]["availability"] == "FULL_TIME"
        assert len(call_args[1]["update_data"]["portfolio"]) == 3


class TestAdminUserServiceDeleteUser:
    """Test delete_user Method"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_delete_customer_with_profile(self, service, mocker):
        """TestDeleteWith Profile 的 Customer"""
        # Mock DAO - Customer Profile Exists
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

        # Provider Profile Does Not Exist
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP Delete响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        result = await service.delete_user(user_id=1)

        # VerifyResult
        assert result is True

        # Verify Customer Profile 被Delete
        service.customer_dao.delete.assert_called_once_with(1)

        # Verify Auth Service DeleteBe Called
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_provider_with_profile(self, service, mocker):
        """TestDeleteWith Profile 的 Provider"""
        # Mock DAO - Provider Profile Exists
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

        # Customer Profile Does Not Exist
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)

        # Mock HTTP Delete响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        result = await service.delete_user(user_id=2)

        # VerifyResult
        assert result is True

        # Verify Provider Profile 被Delete
        service.provider_dao.delete.assert_called_once_with(2)

        # Verify Auth Service DeleteBe Called
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_without_profile(self, service, mocker):
        """TestDeleteWithout Profile 的User(Admin)"""
        # Mock DAO - Both Profile AllDoes Not Exist
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)
        
        # Mock delete Method(Even If Not Called, Still Need ToMock)
        mock_customer_delete = mocker.patch.object(service.customer_dao, "delete")
        mock_provider_delete = mocker.patch.object(service.provider_dao, "delete")

        # Mock HTTP Delete响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        result = await service.delete_user(user_id=3)

        # VerifyResult
        assert result is True

        # Verify DAO delete Not Called
        mock_customer_delete.assert_not_called()
        mock_provider_delete.assert_not_called()

        # Verify Auth Service DeleteStillBe Called
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, service, mocker):
        """TestDeleteDoes Not Exist的User"""
        # Mock DAO - Profile Does Not Exist
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP Return 404
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_user(user_id=999)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_delete_user_auth_service_error(self, service, mocker):
        """TestDelete UserWhen Auth Service ReturnError"""
        # Mock DAO
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        # Mock HTTP Return 500
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.delete.return_value = mock_response

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # ExecuteTest
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_user(user_id=1)

        assert exc_info.value.status_code == 500


class TestAdminUserServiceHelperMethods:
    """TestHelper Method _check_profile_exists And _get_role_name"""

    @pytest.fixture
    def service(self, mock_mongo_db):
        return AdminUserService(mock_mongo_db)

    @pytest.mark.asyncio
    async def test_check_profile_exists_customer_true(self, service, mocker):
        """Test Customer Profile Exists"""
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
        """Test Customer Profile Does Not Exist"""
        mocker.patch.object(service.customer_dao, "get_by_user_id", return_value=None)

        result = await service._check_profile_exists(user_id=1, role_id=1)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_provider_true(self, service, mocker):
        """Test Provider Profile Exists"""
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
        """Test Provider Profile Does Not Exist"""
        mocker.patch.object(service.provider_dao, "get_by_user_id", return_value=None)

        result = await service._check_profile_exists(user_id=2, role_id=2)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_admin_role(self, service):
        """Test Admin Role(No Profile)"""
        result = await service._check_profile_exists(user_id=3, role_id=3)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_profile_exists_unknown_role(self, service):
        """TestUnknownRole"""
        result = await service._check_profile_exists(user_id=4, role_id=99)
        assert result is False

    def test_get_role_name_customer(self, service):
        """TestGet Customer RoleName"""
        assert service._get_role_name(1) == "customer"

    def test_get_role_name_provider(self, service):
        """TestGet Provider RoleName"""
        assert service._get_role_name(2) == "provider"

    def test_get_role_name_admin(self, service):
        """TestGet Admin RoleName"""
        assert service._get_role_name(3) == "admin"

    def test_get_role_name_unknown(self, service):
        """TestUnknownRoleName"""
        assert service._get_role_name(99) == "unknown"
