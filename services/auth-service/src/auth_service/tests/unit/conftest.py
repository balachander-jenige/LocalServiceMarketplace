"""
单元测试通用Fixtures配置
提供Mock对象和测试数据
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from auth_service.core.security import hash_password


@pytest.fixture
def mock_db_session():
    """Mock数据库会话"""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.get = AsyncMock()
    return mock_db


@pytest.fixture
def sample_user_data():
    """标准用户测试数据"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("Test123!"),
        "role_id": 1,
        "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
    }


@pytest.fixture
def sample_customer_data():
    """客户测试数据"""
    return {
        "id": 1,
        "username": "customer1",
        "email": "customer@test.com",
        "password_hash": hash_password("Test123!"),
        "role_id": 1,
    }


@pytest.fixture
def sample_provider_data():
    """服务商测试数据"""
    return {
        "id": 2,
        "username": "provider1",
        "email": "provider@test.com",
        "password_hash": hash_password("Test123!"),
        "role_id": 2,
    }


@pytest.fixture
def sample_admin_data():
    """管理员测试数据"""
    return {
        "id": 3,
        "username": "admin",
        "email": "admin@test.com",
        "password_hash": hash_password("Test123!"),
        "role_id": 3,
    }


@pytest.fixture
def mock_user_object(sample_user_data):
    """Mock User对象"""
    mock_user = MagicMock()
    for key, value in sample_user_data.items():
        setattr(mock_user, key, value)
    return mock_user
