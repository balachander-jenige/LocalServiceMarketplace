"""
CustomerProfileService 单元测试
测试客户资料创建、查询、更新逻辑
"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from user_service.models.customer_profile import CustomerProfile, LocationEnum
from user_service.services.customer_profile_service import CustomerProfileService


class TestCustomerProfileServiceCreate:
    """Test CustomerProfileService.create_profile"""

    @pytest.mark.asyncio
    async def test_create_profile_success(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestCreateCustomerProfileSuccess"""
        # Arrange
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock(spec=CustomerProfile)
        mock_profile.user_id = 1
        mock_profile.location = LocationEnum.NORTH
        mock_profile.address = "123 Test St"
        mock_profile.budget_preference = 100.0

        # Mock DAO
        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        # Act
        result = await service.create_profile(user_id=1, location="NORTH", address="123 Test St", budget_preference=100.0)

        # Assert
        assert result.user_id == 1
        assert result.location == LocationEnum.NORTH
        service.dao.get_by_user_id.assert_awaited_once_with(1)
        service.dao.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_profile_already_exists(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestCreateAlready ExistingCustomerProfile"""
        # Arrange
        service = CustomerProfileService(mock_mongo_db)
        existing_profile = MagicMock()

        mocker.patch.object(service.dao, "get_by_user_id", return_value=existing_profile)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.create_profile(user_id=1, location="NORTH")

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_profile_with_minimal_data(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestOnly Provide Required FieldsCreateProfile"""
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mock_profile.user_id = 1
        mock_profile.location = LocationEnum.SOUTH
        mock_profile.address = None
        mock_profile.budget_preference = 0.0

        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        result = await service.create_profile(user_id=1, location="SOUTH")

        assert result.user_id == 1
        assert result.location == LocationEnum.SOUTH
        assert result.address is None
        assert result.budget_preference == 0.0

    @pytest.mark.asyncio
    async def test_create_profile_publishes_event(self, mock_mongo_db, mocker):
        """TestCreateProfilePublish Event"""
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        mock_publish = mocker.patch(
            "user_service.services.customer_profile_service.EventPublisher.publish_profile_created"
        )

        await service.create_profile(user_id=1, location="NORTH")

        mock_publish.assert_awaited_once()
        call_args = mock_publish.call_args[0][0]
        assert call_args.user_id == 1
        assert call_args.profile_type == "customer"


class TestCustomerProfileServiceGet:
    """Test CustomerProfileService.get_profile"""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, mock_mongo_db, mocker):
        """TestGetCustomerProfileSuccess"""
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mock_profile.user_id = 1
        mocker.patch.object(service.dao, "get_by_user_id", return_value=mock_profile)

        result = await service.get_profile(user_id=1)

        assert result.user_id == 1
        service.dao.get_by_user_id.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, mock_mongo_db, mocker):
        """TestGetDoes Not Exist的CustomerProfile"""
        service = CustomerProfileService(mock_mongo_db)

        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_profile(user_id=999)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


class TestCustomerProfileServiceUpdate:
    """Test CustomerProfileService.update_profile"""

    @pytest.mark.asyncio
    async def test_update_profile_success(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestUpdateCustomerProfileSuccess"""
        service = CustomerProfileService(mock_mongo_db)

        mock_updated_profile = MagicMock()
        mock_updated_profile.user_id = 1
        mock_updated_profile.address = "456 New St"

        mocker.patch.object(service.dao, "update", return_value=mock_updated_profile)

        update_data = {"address": "456 New St", "budget_preference": 200.0}
        result = await service.update_profile(user_id=1, update_data=update_data)

        assert result.user_id == 1
        service.dao.update.assert_awaited_once_with(1, update_data)

    @pytest.mark.asyncio
    async def test_update_profile_not_found(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestUpdateDoes Not Exist的Profile"""
        service = CustomerProfileService(mock_mongo_db)

        mocker.patch.object(service.dao, "update", return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_profile(user_id=999, update_data={"address": "New Address"})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_profile_empty_data(self, mock_mongo_db, mock_event_publisher):
        """TestProvideEmptyDataUpdate"""
        service = CustomerProfileService(mock_mongo_db)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_profile(user_id=1, update_data={})

        assert exc_info.value.status_code == 400
        assert "No data to update" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_profile_filters_none_values(self, mock_mongo_db, mock_event_publisher, mocker):
        """TestFilter None Values"""
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mocker.patch.object(service.dao, "update", return_value=mock_profile)

        update_data = {"address": "New Address", "budget_preference": None, "location": None}
        await service.update_profile(user_id=1, update_data=update_data)

        # VerifyOnly Passed Non-NoneValue
        call_args = service.dao.update.call_args[0]
        assert call_args[1] == {"address": "New Address"}

    @pytest.mark.asyncio
    async def test_update_profile_publishes_event(self, mock_mongo_db, mocker):
        """TestUpdateProfilePublish Event"""
        service = CustomerProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mocker.patch.object(service.dao, "update", return_value=mock_profile)

        mock_publish = mocker.patch(
            "user_service.services.customer_profile_service.EventPublisher.publish_profile_updated"
        )

        update_data = {"address": "New Address"}
        await service.update_profile(user_id=1, update_data=update_data)

        mock_publish.assert_awaited_once()
        call_args = mock_publish.call_args[0][0]
        assert call_args.user_id == 1
        assert call_args.profile_type == "customer"
        assert call_args.updated_fields == update_data
