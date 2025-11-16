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
    """Test密码哈希"""

    def test_hash_password_returns_string(self):
        """TestReturn字符串"""
        hashed = hash_password("Test123!")
        assert isinstance(hashed, str)

    def test_hash_password_bcrypt_format(self):
        """TestbcryptFormat"""
        hashed = hash_password("Test123!")
        assert hashed.startswith("$2b$")

    def test_hash_password_different_inputs_different_outputs(self):
        """TestDifferentInputProduceDifferentOutput"""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2

    def test_hash_password_same_input_different_salts(self):
        """TestSameInputDifferentsalt"""
        hash1 = hash_password("Test123!")
        hash2 = hash_password("Test123!")
        # bcryptEach UseDifferentsalt
        assert hash1 != hash2


class TestPasswordVerification:
    """Test密码Verify"""

    def test_verify_password_correct(self):
        """TestCorrect密码"""
        hashed = hash_password("Test123!")
        assert verify_password("Test123!", hashed) is True

    def test_verify_password_incorrect(self):
        """TestError密码"""
        hashed = hash_password("Test123!")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_case_sensitive(self):
        """TestCaseSensitive"""
        hashed = hash_password("Test123!")
        assert verify_password("test123!", hashed) is False

    def test_verify_password_empty_password(self):
        """TestEmpty密码"""
        hashed = hash_password("Test123!")
        assert verify_password("", hashed) is False


class TestJWTTokenCreation:
    """TestJWTCreate"""

    def test_create_token_returns_string(self):
        """TestReturn字符串"""
        token = create_access_token({"sub": "1", "role": 1})
        assert isinstance(token, str)

    def test_create_token_can_be_decoded(self):
        """TesttokenCan Decode"""
        token = create_access_token({"sub": "1", "role": 1})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == 1

    def test_create_token_includes_expiration(self):
        """TestContainsExpiration Time"""
        token = create_access_token({"sub": "1"})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload
        # VerifyExpiration TimeIn Future
        assert payload["exp"] > datetime.now(UTC).timestamp()

    def test_create_token_custom_expiration(self):
        """TestCustomExpiration Time"""
        custom_delta = timedelta(minutes=5)
        token = create_access_token({"sub": "1"}, expires_delta=custom_delta)
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # VerifyExpiration TimeAbout5Minutes Later
        expected_exp = (datetime.now(UTC) + custom_delta).timestamp()
        assert abs(payload["exp"] - expected_exp) < 2  # Allow2Seconds Error

    def test_create_token_with_multiple_claims(self):
        """TestContainsMultipleClaims"""
        token = create_access_token({"sub": "1", "role": 1, "username": "testuser"})
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == 1
        assert payload["username"] == "testuser"


class TestJWTTokenVerification:
    """TestJWTVerify"""

    def test_verify_token_valid(self):
        """TestValidtoken"""
        token = create_access_token({"sub": "1", "role": 1})
        credentials = MagicMock()
        credentials.credentials = token

        payload = verify_token(credentials)
        assert payload["sub"] == "1"
        assert payload["role"] == 1

    def test_verify_token_expired(self):
        """TestExpiredtoken"""
        # CreateExpiredtoken
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-10))
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401

    def test_verify_token_invalid_signature(self):
        """TestSignatureError的token"""
        # Created With Wrong Keytoken
        fake_token = jwt.encode({"sub": "1"}, "wrong_secret_key", algorithm="HS256")
        credentials = MagicMock()
        credentials.credentials = fake_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401

    def test_verify_token_malformed(self):
        """TestMalformedtoken"""
        credentials = MagicMock()
        credentials.credentials = "not.a.valid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
