"""
ProviderProfileService 单元测试
测试服务商资料创建、查询、更新、搜索逻辑
"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from user_service.models.provider_profile import ProviderProfile
from user_service.services.provider_profile_service import ProviderProfileService


class TestProviderProfileServiceCreate:
    """测试 ProviderProfileService.create_profile"""

    @pytest.mark.asyncio
    async def test_create_profile_success(self, mock_mongo_db, mock_event_publisher, mocker):
        """测试创建服务商资料成功"""
        service = ProviderProfileService(mock_mongo_db)

        mock_profile = MagicMock(spec=ProviderProfile)
        mock_profile.user_id = 2
        mock_profile.skills = ["Python", "FastAPI"]
        mock_profile.experience_years = 5
        mock_profile.hourly_rate = 50.0

        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        result = await service.create_profile(
            user_id=2, skills=["Python", "FastAPI"], experience_years=5, hourly_rate=50.0, availability="Full-time"
        )

        assert result.user_id == 2
        assert result.skills == ["Python", "FastAPI"]
        service.dao.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_profile_already_exists(self, mock_mongo_db, mock_event_publisher, mocker):
        """测试创建已存在的服务商资料"""
        service = ProviderProfileService(mock_mongo_db)

        mocker.patch.object(service.dao, "get_by_user_id", return_value=MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            await service.create_profile(user_id=2, skills=["Python"])

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_profile_with_defaults(self, mock_mongo_db, mock_event_publisher, mocker):
        """测试使用默认值创建资料"""
        service = ProviderProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mock_profile.user_id = 2
        mock_profile.skills = []
        mock_profile.experience_years = 0
        mock_profile.hourly_rate = 0.0
        mock_profile.rating = 5.0
        mock_profile.total_reviews = 0

        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        result = await service.create_profile(user_id=2)

        assert result.skills == []
        assert result.experience_years == 0
        assert result.rating == 5.0
        assert result.total_reviews == 0

    @pytest.mark.asyncio
    async def test_create_profile_publishes_event(self, mock_mongo_db, mocker):
        """测试创建资料发布事件"""
        service = ProviderProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
        mocker.patch.object(service.dao, "create", return_value=mock_profile)

        mock_publish = mocker.patch(
            "user_service.services.provider_profile_service.EventPublisher.publish_profile_created"
        )

        await service.create_profile(user_id=2, skills=["Python"])

        mock_publish.assert_awaited_once()
        call_args = mock_publish.call_args[0][0]
        assert call_args.user_id == 2
        assert call_args.profile_type == "provider"


class TestProviderProfileServiceGet:
    """测试 ProviderProfileService.get_profile"""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, mock_mongo_db, mocker):
        """测试获取服务商资料成功"""
        service = ProviderProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mock_profile.user_id = 2
        mocker.patch.object(service.dao, "get_by_user_id", return_value=mock_profile)

        result = await service.get_profile(user_id=2)

        assert result.user_id == 2
        service.dao.get_by_user_id.assert_awaited_once_with(2)

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, mock_mongo_db, mocker):
        """测试获取不存在的服务商资料"""
        service = ProviderProfileService(mock_mongo_db)

        mocker.patch.object(service.dao, "get_by_user_id", return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_profile(user_id=999)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


class TestProviderProfileServiceUpdate:
    """测试 ProviderProfileService.update_profile"""

    @pytest.mark.asyncio
    async def test_update_profile_success(self, mock_mongo_db, mock_event_publisher, mocker):
        """测试更新服务商资料成功"""
        service = ProviderProfileService(mock_mongo_db)

        mock_updated_profile = MagicMock()
        mock_updated_profile.user_id = 2
        mock_updated_profile.hourly_rate = 75.0

        mocker.patch.object(service.dao, "update", return_value=mock_updated_profile)

        update_data = {"hourly_rate": 75.0, "skills": ["Python", "Django"]}
        result = await service.update_profile(user_id=2, update_data=update_data)

        assert result.user_id == 2
        service.dao.update.assert_awaited_once_with(2, update_data)

    @pytest.mark.asyncio
    async def test_update_profile_not_found(self, mock_mongo_db, mock_event_publisher, mocker):
        """测试更新不存在的资料"""
        service = ProviderProfileService(mock_mongo_db)

        mocker.patch.object(service.dao, "update", return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_profile(user_id=999, update_data={"hourly_rate": 75.0})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_profile_empty_data(self, mock_mongo_db, mock_event_publisher):
        """测试提供空数据更新"""
        service = ProviderProfileService(mock_mongo_db)

        with pytest.raises(HTTPException) as exc_info:
            await service.update_profile(user_id=2, update_data={})

        assert exc_info.value.status_code == 400
        assert "No data to update" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_profile_publishes_event(self, mock_mongo_db, mocker):
        """测试更新资料发布事件"""
        service = ProviderProfileService(mock_mongo_db)

        mock_profile = MagicMock()
        mocker.patch.object(service.dao, "update", return_value=mock_profile)

        mock_publish = mocker.patch(
            "user_service.services.provider_profile_service.EventPublisher.publish_profile_updated"
        )

        update_data = {"hourly_rate": 75.0}
        await service.update_profile(user_id=2, update_data=update_data)

        mock_publish.assert_awaited_once()


class TestProviderProfileServiceSearch:
    """测试 ProviderProfileService.search_providers"""

    @pytest.mark.asyncio
    async def test_search_providers_no_filters(self, mock_mongo_db, mocker):
        """测试无过滤条件搜索"""
        service = ProviderProfileService(mock_mongo_db)

        mock_providers = [MagicMock(), MagicMock()]
        mocker.patch.object(service.dao, "search_providers", return_value=mock_providers)

        result = await service.search_providers()

        assert len(result) == 2
        service.dao.search_providers.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_search_providers_with_skills(self, mock_mongo_db, mocker):
        """测试按技能搜索"""
        service = ProviderProfileService(mock_mongo_db)

        mock_providers = [MagicMock()]
        mocker.patch.object(service.dao, "search_providers", return_value=mock_providers)

        result = await service.search_providers(skills=["Python", "FastAPI"])

        assert len(result) == 1
        call_kwargs = service.dao.search_providers.call_args.kwargs
        assert call_kwargs["skills"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_search_providers_with_rating_filter(self, mock_mongo_db, mocker):
        """测试按评分过滤"""
        service = ProviderProfileService(mock_mongo_db)

        mock_providers = [MagicMock()]
        mocker.patch.object(service.dao, "search_providers", return_value=mock_providers)

        result = await service.search_providers(min_rating=4.0)

        call_kwargs = service.dao.search_providers.call_args.kwargs
        assert call_kwargs["min_rating"] == 4.0

    @pytest.mark.asyncio
    async def test_search_providers_with_hourly_rate_limit(self, mock_mongo_db, mocker):
        """测试按时薪上限过滤"""
        service = ProviderProfileService(mock_mongo_db)

        mock_providers = [MagicMock()]
        mocker.patch.object(service.dao, "search_providers", return_value=mock_providers)

        result = await service.search_providers(max_hourly_rate=100.0)

        call_kwargs = service.dao.search_providers.call_args.kwargs
        assert call_kwargs["max_hourly_rate"] == 100.0

    @pytest.mark.asyncio
    async def test_search_providers_with_custom_limit(self, mock_mongo_db, mocker):
        """测试自定义返回数量"""
        service = ProviderProfileService(mock_mongo_db)

        mock_providers = [MagicMock() for _ in range(10)]
        mocker.patch.object(service.dao, "search_providers", return_value=mock_providers)

        result = await service.search_providers(limit=10)

        assert len(result) == 10
        call_kwargs = service.dao.search_providers.call_args.kwargs
        assert call_kwargs["limit"] == 10
