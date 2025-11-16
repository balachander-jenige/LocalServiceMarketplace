"""
AdminUserService 单元测试
测试管理员用户管理逻辑(HTTP调用Mock)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from user_service.services.admin_user_service import AdminUserService


class TestAdminUserServiceGetAllUsers:
    """Test AdminUserService.get_all_users"""

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, mock_mongo_db, mocker):
        """TestGetAllUserSuccess"""
        service = AdminUserService(mock_mongo_db)

        # Mock HTTP response
        mock_users = [
            {"id": 1, "username": "user1", "email": "user1@test.com", "role_id": 1, "created_at": "2025-01-01"},
            {"id": 2, "username": "user2", "email": "user2@test.com", "role_id": 2, "created_at": "2025-01-02"},
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_users

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)
        
        # Mock _check_profile_exists to return awaitable
        async def mock_check_profile(user_id, role_id):
            return True
        
        mocker.patch.object(service, "_check_profile_exists", side_effect=mock_check_profile)
        mocker.patch.object(service, "_get_role_name", side_effect=lambda x: "Customer" if x == 1 else "Provider")

        # Act
        result = await service.get_all_users()

        # Assert
        assert len(result) == 2
        assert result[0]["user_id"] == 1
        assert result[0]["username"] == "user1"
        assert result[0]["role_name"] == "Customer"
        assert result[1]["role_name"] == "Provider"

    @pytest.mark.asyncio
    async def test_get_all_users_with_role_filter(self, mock_mongo_db, mocker):
        """TestByRoleFilterUser"""
        service = AdminUserService(mock_mongo_db)

        mock_users = [{"id": 1, "username": "user1", "email": "user1@test.com", "role_id": 1, "created_at": "2025-01-01"}]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_users

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)
        
        async def mock_check_profile(user_id, role_id):
            return True
        
        mocker.patch.object(service, "_check_profile_exists", side_effect=mock_check_profile)
        mocker.patch.object(service, "_get_role_name", return_value="Customer")

        result = await service.get_all_users(role_filter=1)

        # VerifyparamsContainsrole_id
        call_kwargs = mock_client.get.call_args.kwargs
        assert call_kwargs["params"] == {"role_id": 1}

    @pytest.mark.asyncio
    async def test_get_all_users_auth_service_error(self, mock_mongo_db, mocker):
        """TestAuth ServiceReturnError"""
        service = AdminUserService(mock_mongo_db)

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_all_users()

        assert exc_info.value.status_code == 500


class TestAdminUserServiceGetUserDetail:
    """Test AdminUserService.get_user_detail"""

    @pytest.mark.asyncio
    async def test_get_customer_detail_with_profile(self, mock_mongo_db, mocker):
        """TestGetWithProfile的CustomerDetails"""
        service = AdminUserService(mock_mongo_db)

        # Mock Auth Service response
        mock_user = {"id": 1, "username": "customer1", "email": "customer@test.com", "role_id": 1, "created_at": "2025-01-01"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Mock customer profile
        mock_profile = MagicMock()
        mock_profile.model_dump.return_value = {
            "user_id": 1,
            "location": "NORTH",
            "address": "123 Test St",
            "budget_preference": 100.0,
        }
        
        async def mock_get_customer(user_id):
            return mock_profile
        
        mocker.patch.object(service.customer_dao, "get_by_user_id", side_effect=mock_get_customer)
        mocker.patch.object(service, "_get_role_name", return_value="Customer")

        # Act
        result = await service.get_user_detail(user_id=1)

        # Assert
        assert result["user_id"] == 1
        assert result["username"] == "customer1"
        assert result["role_name"] == "Customer"
        assert result["profile"]["location"] == "NORTH"

    @pytest.mark.asyncio
    async def test_get_customer_detail_without_profile(self, mock_mongo_db, mocker):
        """TestGetNoProfile的CustomerDetails(ReturnDefault Value)"""
        service = AdminUserService(mock_mongo_db)

        mock_user = {"id": 1, "username": "customer1", "email": "customer@test.com", "role_id": 1, "created_at": "2025-01-01"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)
        
        async def mock_get_customer(user_id):
            return None
        
        mocker.patch.object(service.customer_dao, "get_by_user_id", side_effect=mock_get_customer)
        mocker.patch.object(service, "_get_role_name", return_value="Customer")

        result = await service.get_user_detail(user_id=1)

        # VerifyReturn默认Profile
        assert result["profile"]["user_id"] == 1
        assert result["profile"]["location"] == "NORTH"
        assert result["profile"]["address"] is None
        assert result["profile"]["budget_preference"] == 0.0

    @pytest.mark.asyncio
    async def test_get_provider_detail_with_profile(self, mock_mongo_db, mocker):
        """TestGetWithProfile的ProviderDetails"""
        service = AdminUserService(mock_mongo_db)

        mock_user = {"id": 2, "username": "provider1", "email": "provider@test.com", "role_id": 2, "created_at": "2025-01-01"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        mock_profile = MagicMock()
        mock_profile.model_dump.return_value = {
            "user_id": 2,
            "skills": ["Python"],
            "experience_years": 5,
            "hourly_rate": 50.0,
            "rating": 4.5,
            "total_reviews": 10,
        }
        
        async def mock_get_provider(user_id):
            return mock_profile
        
        mocker.patch.object(service.provider_dao, "get_by_user_id", side_effect=mock_get_provider)
        mocker.patch.object(service, "_get_role_name", return_value="Provider")

        result = await service.get_user_detail(user_id=2)

        assert result["profile"]["skills"] == ["Python"]
        assert result["profile"]["rating"] == 4.5

    @pytest.mark.asyncio
    async def test_get_provider_detail_without_profile(self, mock_mongo_db, mocker):
        """TestGetNoProfile的ProviderDetails(ReturnDefault Value)"""
        service = AdminUserService(mock_mongo_db)

        mock_user = {"id": 2, "username": "provider1", "email": "provider@test.com", "role_id": 2, "created_at": "2025-01-01"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)
        
        async def mock_get_provider(user_id):
            return None
        
        mocker.patch.object(service.provider_dao, "get_by_user_id", side_effect=mock_get_provider)
        mocker.patch.object(service, "_get_role_name", return_value="Provider")

        result = await service.get_user_detail(user_id=2)

        # VerifyReturn默认Provider Profile
        assert result["profile"]["skills"] == []
        assert result["profile"]["experience_years"] == 0
        assert result["profile"]["rating"] == 5.0
        assert result["profile"]["total_reviews"] == 0

    @pytest.mark.asyncio
    async def test_get_user_detail_not_found(self, mock_mongo_db, mocker):
        """TestGetDoes Not Exist的User"""
        service = AdminUserService(mock_mongo_db)

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_user_detail(user_id=999)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail
