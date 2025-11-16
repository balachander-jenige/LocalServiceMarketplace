"""
ProviderProfileDAO 单元测试
测试MongoDB CRUD操作和复杂查询
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from user_service.dao.provider_profile_dao import ProviderProfileDAO
from user_service.models.provider_profile import ProviderProfile


class TestProviderProfileDAOCreate:
    """Test ProviderProfileDAO.create"""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_mongo_db, sample_provider_profile):
        """TestCreateProviderProfileSuccess"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_mongo_db["provider_profiles"].insert_one = AsyncMock()

        result = await dao.create(sample_provider_profile)

        assert result == sample_provider_profile
        mock_mongo_db["provider_profiles"].insert_one.assert_awaited_once()
        call_args = mock_mongo_db["provider_profiles"].insert_one.call_args[0][0]
        assert call_args["user_id"] == 2
        assert call_args["skills"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, mock_mongo_db):
        """TestCreateContainsAllFields的ProviderProfile"""
        dao = ProviderProfileDAO(mock_mongo_db)

        profile = ProviderProfile(
            user_id=2,
            skills=["Python", "FastAPI", "MongoDB"],
            experience_years=5,
            hourly_rate=75.0,
            availability="Full-time",
            portfolio=["https://github.com/test"],
            rating=4.8,
            total_reviews=25,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_mongo_db["provider_profiles"].insert_one = AsyncMock()

        result = await dao.create(profile)

        assert result.experience_years == 5
        assert result.hourly_rate == 75.0
        assert result.rating == 4.8


class TestProviderProfileDAOGet:
    """Test ProviderProfileDAO.get_by_user_id"""

    @pytest.mark.asyncio
    async def test_get_by_user_id_success(self, mock_mongo_db):
        """TestQueryProviderProfileSuccess"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_doc = {
            "_id": "mock_id",
            "user_id": 2,
            "skills": ["Python", "FastAPI"],
            "experience_years": 3,
            "hourly_rate": 50.0,
            "availability": "Part-time",
            "portfolio": [],
            "rating": 4.5,
            "total_reviews": 10,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_mongo_db["provider_profiles"].find_one = AsyncMock(return_value=mock_doc)

        result = await dao.get_by_user_id(2)

        assert result is not None
        assert result.user_id == 2
        assert result.skills == ["Python", "FastAPI"]
        assert result.hourly_rate == 50.0
        assert "_id" not in result.model_dump()
        mock_mongo_db["provider_profiles"].find_one.assert_awaited_once_with({"user_id": 2})

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, mock_mongo_db):
        """TestQueryDoes Not Exist的ProviderProfile"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_mongo_db["provider_profiles"].find_one = AsyncMock(return_value=None)

        result = await dao.get_by_user_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_removes_mongodb_id(self, mock_mongo_db):
        """TestReturnResult移除MongoDB _idFields"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "user_id": 2,
            "skills": [],
            "experience_years": 0,
            "hourly_rate": 0.0,
            "availability": None,
            "portfolio": [],
            "rating": 5.0,
            "total_reviews": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_mongo_db["provider_profiles"].find_one = AsyncMock(return_value=mock_doc)

        result = await dao.get_by_user_id(2)

        assert result is not None
        assert "_id" not in result.model_dump()


class TestProviderProfileDAOUpdate:
    """Test ProviderProfileDAO.update"""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_mongo_db, mocker):
        """TestUpdateProviderProfileSuccess"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_mongo_db["provider_profiles"].update_one = AsyncMock(return_value=mock_result)

        updated_profile = ProviderProfile(
            user_id=2,
            skills=["Python", "Django"],
            experience_years=5,
            hourly_rate=75.0,
            availability="Full-time",
            portfolio=[],
            rating=5.0,
            total_reviews=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mocker.patch.object(dao, "get_by_user_id", return_value=updated_profile)

        update_data = {"hourly_rate": 75.0, "skills": ["Python", "Django"]}
        result = await dao.update(2, update_data)

        assert result is not None
        assert result.hourly_rate == 75.0
        assert result.skills == ["Python", "Django"]

        mock_mongo_db["provider_profiles"].update_one.assert_awaited_once()
        call_args = mock_mongo_db["provider_profiles"].update_one.call_args
        assert call_args[0][0] == {"user_id": 2}
        assert "updated_at" in call_args[0][1]["$set"]

    @pytest.mark.asyncio
    async def test_update_not_found(self, mock_mongo_db):
        """TestUpdateDoes Not Exist的Profile"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_mongo_db["provider_profiles"].update_one = AsyncMock(return_value=mock_result)

        result = await dao.update(999, {"hourly_rate": 75.0})

        assert result is None

    @pytest.mark.asyncio
    async def test_update_adds_timestamp(self, mock_mongo_db, mocker):
        """TestUpdate自动添加updated_atWhen间戳"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_mongo_db["provider_profiles"].update_one = AsyncMock(return_value=mock_result)

        mocker.patch.object(
            dao,
            "get_by_user_id",
            return_value=ProviderProfile(
                user_id=2,
                skills=[],
                experience_years=0,
                hourly_rate=50.0,
                availability=None,
                portfolio=[],
                rating=5.0,
                total_reviews=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        )

        update_data = {"hourly_rate": 75.0}
        await dao.update(2, update_data)

        call_args = mock_mongo_db["provider_profiles"].update_one.call_args[0][1]["$set"]
        assert "updated_at" in call_args
        assert isinstance(call_args["updated_at"], datetime)


class TestProviderProfileDAODelete:
    """Test ProviderProfileDAO.delete"""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_mongo_db):
        """TestDeleteSuccess"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_mongo_db["provider_profiles"].delete_one = AsyncMock(return_value=mock_result)

        result = await dao.delete(2)

        assert result is True
        mock_mongo_db["provider_profiles"].delete_one.assert_awaited_once_with({"user_id": 2})

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_mongo_db):
        """TestDeleteDoes Not Exist的Profile"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_result = MagicMock()
        mock_result.deleted_count = 0
        mock_mongo_db["provider_profiles"].delete_one = AsyncMock(return_value=mock_result)

        result = await dao.delete(999)

        assert result is False


class TestProviderProfileDAOSearch:
    """Test ProviderProfileDAO.search_providers (复杂Query)"""

    @pytest.mark.asyncio
    async def test_search_no_filters(self, mock_mongo_db):
        """TestNoFilter条件Search"""
        dao = ProviderProfileDAO(mock_mongo_db)

        # Mock cursor
        mock_docs = [
            {
                "_id": "id1",
                "user_id": 2,
                "skills": ["Python"],
                "experience_years": 3,
                "hourly_rate": 50.0,
                "availability": None,
                "portfolio": [],
                "rating": 4.5,
                "total_reviews": 10,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": "id2",
                "user_id": 3,
                "skills": ["JavaScript"],
                "experience_years": 5,
                "hourly_rate": 75.0,
                "availability": None,
                "portfolio": [],
                "rating": 4.8,
                "total_reviews": 20,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        result = await dao.search_providers()

        assert len(result) == 2
        assert result[0].user_id == 2
        assert result[1].user_id == 3
        # VerifyCallfind({})
        mock_mongo_db["provider_profiles"].find.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_search_with_skills_filter(self, mock_mongo_db):
        """TestBySkillsSearch"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = [
            {
                "_id": "id1",
                "user_id": 2,
                "skills": ["Python", "FastAPI"],
                "experience_years": 3,
                "hourly_rate": 50.0,
                "availability": None,
                "portfolio": [],
                "rating": 4.5,
                "total_reviews": 10,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        ]

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        result = await dao.search_providers(skills=["Python", "FastAPI"])

        assert len(result) == 1
        assert result[0].skills == ["Python", "FastAPI"]
        # VerifyQuery条件
        call_args = mock_mongo_db["provider_profiles"].find.call_args[0][0]
        assert call_args == {"skills": {"$in": ["Python", "FastAPI"]}}

    @pytest.mark.asyncio
    async def test_search_with_min_rating_filter(self, mock_mongo_db):
        """TestBy最低RatingFilter"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = []
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        await dao.search_providers(min_rating=4.5)

        # VerifyQuery条件Contains$gte
        call_args = mock_mongo_db["provider_profiles"].find.call_args[0][0]
        assert call_args == {"rating": {"$gte": 4.5}}

    @pytest.mark.asyncio
    async def test_search_with_max_hourly_rate_filter(self, mock_mongo_db):
        """TestByHourly Rate上限Filter"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = []
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        await dao.search_providers(max_hourly_rate=100.0)

        # VerifyQuery条件Contains$lte
        call_args = mock_mongo_db["provider_profiles"].find.call_args[0][0]
        assert call_args == {"hourly_rate": {"$lte": 100.0}}

    @pytest.mark.asyncio
    async def test_search_with_multiple_filters(self, mock_mongo_db):
        """Test组合MultipleFilter条件"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = []
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        await dao.search_providers(skills=["Python"], min_rating=4.0, max_hourly_rate=80.0)

        # Verify复合Query条件
        call_args = mock_mongo_db["provider_profiles"].find.call_args[0][0]
        assert call_args["skills"] == {"$in": ["Python"]}
        assert call_args["rating"] == {"$gte": 4.0}
        assert call_args["hourly_rate"] == {"$lte": 80.0}

    @pytest.mark.asyncio
    async def test_search_with_custom_limit(self, mock_mongo_db):
        """TestCustomReturn数量限制"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = []
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        await dao.search_providers(limit=50)

        # VerifylimitBe Set Correctly
        mock_cursor.limit.assert_called_once_with(50)
        mock_cursor.to_list.assert_awaited_once_with(length=50)

    @pytest.mark.asyncio
    async def test_search_removes_mongodb_ids(self, mock_mongo_db):
        """TestSearchResult移除AllMongoDB _idFields"""
        dao = ProviderProfileDAO(mock_mongo_db)

        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": 2,
                "skills": ["Python"],
                "experience_years": 3,
                "hourly_rate": 50.0,
                "availability": None,
                "portfolio": [],
                "rating": 4.5,
                "total_reviews": 10,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": "507f1f77bcf86cd799439012",
                "user_id": 3,
                "skills": ["JavaScript"],
                "experience_years": 5,
                "hourly_rate": 75.0,
                "availability": None,
                "portfolio": [],
                "rating": 4.8,
                "total_reviews": 20,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_mongo_db["provider_profiles"].find = MagicMock(return_value=mock_cursor)

        result = await dao.search_providers()

        # VerifyAllResultAllWithout_id
        for profile in result:
            assert "_id" not in profile.model_dump()
