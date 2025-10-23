"""
Security工具函数单元测试
测试密码加密、验证和JWT处理
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from auth_service.core.config import settings
from auth_service.core.security import create_access_token, hash_password, verify_password, verify_token


class TestPasswordHashing:
    """测试密码哈希"""

    def test_hash_password_returns_string(self):
        """测试返回字符串"""
        hashed = hash_password("Test123!")
        assert isinstance(hashed, str)

    def test_hash_password_bcrypt_format(self):
        """测试bcrypt格式"""
        hashed = hash_password("Test123!")
        assert hashed.startswith("$2b$")

    def test_hash_password_different_inputs_different_outputs(self):
        """测试不同输入产生不同输出"""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2

    def test_hash_password_same_input_different_salts(self):
        """测试相同输入不同salt"""
        hash1 = hash_password("Test123!")
        hash2 = hash_password("Test123!")
        # bcrypt每次使用不同salt
        assert hash1 != hash2


class TestPasswordVerification:
    """测试密码验证"""

    def test_verify_password_correct(self):
        """测试正确密码"""
        hashed = hash_password("Test123!")
        assert verify_password("Test123!", hashed) is True

    def test_verify_password_incorrect(self):
        """测试错误密码"""
        hashed = hash_password("Test123!")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_case_sensitive(self):
        """测试大小写敏感"""
        hashed = hash_password("Test123!")
        assert verify_password("test123!", hashed) is False

    def test_verify_password_empty_password(self):
        """测试空密码"""
        hashed = hash_password("Test123!")
        assert verify_password("", hashed) is False


class TestJWTTokenCreation:
    """测试JWT创建"""

    def test_create_token_returns_string(self):
        """测试返回字符串"""
        token = create_access_token({"sub": "1", "role": 1})
        assert isinstance(token, str)

    def test_create_token_can_be_decoded(self):
        """测试token可解码"""
        token = create_access_token({"sub": "1", "role": 1})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == 1

    def test_create_token_includes_expiration(self):
        """测试包含过期时间"""
        token = create_access_token({"sub": "1"})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload
        # 验证过期时间在未来
        assert payload["exp"] > datetime.now(UTC).timestamp()

    def test_create_token_custom_expiration(self):
        """测试自定义过期时间"""
        custom_delta = timedelta(minutes=5)
        token = create_access_token({"sub": "1"}, expires_delta=custom_delta)
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # 验证过期时间约为5分钟后
        expected_exp = (datetime.now(UTC) + custom_delta).timestamp()
        assert abs(payload["exp"] - expected_exp) < 2  # 允许2秒误差

    def test_create_token_with_multiple_claims(self):
        """测试包含多个声明"""
        token = create_access_token({"sub": "1", "role": 1, "username": "testuser"})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == 1
        assert payload["username"] == "testuser"


class TestJWTTokenVerification:
    """测试JWT验证"""

    def test_verify_token_valid(self):
        """测试有效token"""
        token = create_access_token({"sub": "1", "role": 1})
        credentials = MagicMock()
        credentials.credentials = token

        payload = verify_token(credentials)
        assert payload["sub"] == "1"
        assert payload["role"] == 1

    def test_verify_token_expired(self):
        """测试过期token"""
        # 创建已过期的token
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-10))
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401

    def test_verify_token_invalid_signature(self):
        """测试签名错误的token"""
        # 使用错误的密钥创建token
        fake_token = jwt.encode({"sub": "1"}, "wrong_secret_key", algorithm="HS256")
        credentials = MagicMock()
        credentials.credentials = fake_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401

    def test_verify_token_malformed(self):
        """测试格式错误的token"""
        credentials = MagicMock()
        credentials.credentials = "not.a.valid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
