"""
CustomerProfileDAO 单元测试
测试MongoDB CRUD操作
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from user_service.dao.customer_profile_dao import CustomerProfileDAO
from user_service.models.customer_profile import CustomerProfile


class TestCustomerProfileDAOCreate:
    """测试 CustomerProfileDAO.create"""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_mongo_db, sample_customer_profile):
        """测试创建客户资料成功"""
        dao = CustomerProfileDAO(mock_mongo_db)

        # Mock insert_one
        mock_mongo_db["customer_profiles"].insert_one = AsyncMock()

        result = await dao.create(sample_customer_profile)

        # 验证
        assert result == sample_customer_profile
        mock_mongo_db["customer_profiles"].insert_one.assert_awaited_once()
        call_args = mock_mongo_db["customer_profiles"].insert_one.call_args[0][0]
        assert call_args["user_id"] == 1
        assert call_args["location"] == "NORTH"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, mock_mongo_db):
        """测试创建包含所有字段的资料"""
        dao = CustomerProfileDAO(mock_mongo_db)

        profile = CustomerProfile(
            user_id=1,
            location="NORTH",
            address="123 Test St",
            budget_preference=500.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_mongo_db["customer_profiles"].insert_one = AsyncMock()

        result = await dao.create(profile)

        assert result.address == "123 Test St"
        assert result.budget_preference == 500.0


class TestCustomerProfileDAOGet:
    """测试 CustomerProfileDAO.get_by_user_id"""

    @pytest.mark.asyncio
    async def test_get_by_user_id_success(self, mock_mongo_db):
        """测试查询成功"""
        dao = CustomerProfileDAO(mock_mongo_db)

        # Mock find_one返回文档
        mock_doc = {
            "_id": "mock_id",
            "user_id": 1,
            "location": "NORTH",
            "address": "123 Test St",
            "budget_preference": 100.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_mongo_db["customer_profiles"].find_one = AsyncMock(return_value=mock_doc)

        result = await dao.get_by_user_id(1)

        # 验证
        assert result is not None
        assert result.user_id == 1
        assert result.location == "NORTH"
        assert result.address == "123 Test St"
        assert "_id" not in result.model_dump()  # 验证_id被移除
        mock_mongo_db["customer_profiles"].find_one.assert_awaited_once_with({"user_id": 1})

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, mock_mongo_db):
        """测试查询不存在的资料"""
        dao = CustomerProfileDAO(mock_mongo_db)

        mock_mongo_db["customer_profiles"].find_one = AsyncMock(return_value=None)

        result = await dao.get_by_user_id(999)

        assert result is None
        mock_mongo_db["customer_profiles"].find_one.assert_awaited_once_with({"user_id": 999})

    @pytest.mark.asyncio
    async def test_get_removes_mongodb_id(self, mock_mongo_db):
        """测试返回结果移除MongoDB _id字段"""
        dao = CustomerProfileDAO(mock_mongo_db)

        mock_doc = {
            "_id": "507f1f77bcf86cd799439011",  # MongoDB ObjectId
            "user_id": 1,
            "location": "NORTH",
            "address": None,
            "budget_preference": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_mongo_db["customer_profiles"].find_one = AsyncMock(return_value=mock_doc)

        result = await dao.get_by_user_id(1)

        # 验证_id不在模型中
        assert result is not None
        result_dict = result.model_dump()
        assert "_id" not in result_dict


class TestCustomerProfileDAOUpdate:
    """测试 CustomerProfileDAO.update"""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_mongo_db, mocker):
        """测试更新成功"""
        dao = CustomerProfileDAO(mock_mongo_db)

        # Mock update_one
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_mongo_db["customer_profiles"].update_one = AsyncMock(return_value=mock_result)

        # Mock get_by_user_id (被update调用)
        updated_profile = CustomerProfile(
            user_id=1,
            location="SOUTH",
            address="456 New St",
            budget_preference=200.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(dao, "get_by_user_id", return_value=updated_profile)

        update_data = {"location": "SOUTH", "address": "456 New St"}
        result = await dao.update(1, update_data)

        # 验证
        assert result is not None
        assert result.location == "SOUTH"
        assert result.address == "456 New St"

        # 验证update_one被调用
        mock_mongo_db["customer_profiles"].update_one.assert_awaited_once()
        call_args = mock_mongo_db["customer_profiles"].update_one.call_args
        assert call_args[0][0] == {"user_id": 1}
        assert "updated_at" in call_args[0][1]["$set"]

    @pytest.mark.asyncio
    async def test_update_not_found(self, mock_mongo_db, mocker):
        """测试更新不存在的资料"""
        dao = CustomerProfileDAO(mock_mongo_db)

        # Mock update_one返回0
        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_mongo_db["customer_profiles"].update_one = AsyncMock(return_value=mock_result)

        update_data = {"location": "SOUTH"}
        result = await dao.update(999, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_adds_timestamp(self, mock_mongo_db, mocker):
        """测试更新自动添加updated_at时间戳"""
        dao = CustomerProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_mongo_db["customer_profiles"].update_one = AsyncMock(return_value=mock_result)

        mocker.patch.object(
            dao,
            "get_by_user_id",
            return_value=CustomerProfile(
                user_id=1,
                location="NORTH",
                address=None,
                budget_preference=0.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        )

        update_data = {"location": "SOUTH"}
        await dao.update(1, update_data)

        # 验证$set包含updated_at
        call_args = mock_mongo_db["customer_profiles"].update_one.call_args[0][1]["$set"]
        assert "updated_at" in call_args
        assert isinstance(call_args["updated_at"], datetime)


class TestCustomerProfileDAODelete:
    """测试 CustomerProfileDAO.delete"""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_mongo_db):
        """测试删除成功"""
        dao = CustomerProfileDAO(mock_mongo_db)

        # Mock delete_one
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_mongo_db["customer_profiles"].delete_one = AsyncMock(return_value=mock_result)

        result = await dao.delete(1)

        assert result is True
        mock_mongo_db["customer_profiles"].delete_one.assert_awaited_once_with({"user_id": 1})

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_mongo_db):
        """测试删除不存在的资料"""
        dao = CustomerProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.deleted_count = 0
        mock_mongo_db["customer_profiles"].delete_one = AsyncMock(return_value=mock_result)

        result = await dao.delete(999)

        assert result is False
