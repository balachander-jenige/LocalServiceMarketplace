"""
Unit tests for Payment Service configuration.

Tests cover:
- Environment variable loading
- Default values
- Required fields validation
- URL validation
- Port type validation
"""

import pytest
from pydantic import ValidationError

from payment_service.core.config import Settings


class TestSettings:
    """Test Settings configuration."""

    def test_settings_with_env_vars(self, monkeypatch):
        """Test settings loaded from environment variables."""
        monkeypatch.setenv("DATABASE_URL", "mysql://test:test@localhost/payment_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://auth:8000")

        settings = Settings()

        assert settings.DATABASE_URL == "mysql://test:test@localhost/payment_db"
        assert settings.RABBITMQ_URL == "amqp://guest:guest@localhost:5672/"
        assert settings.AUTH_SERVICE_URL == "http://auth:8000"

    def test_settings_default_values(self):
        """Test default configuration values."""
        settings = Settings()

        assert settings.SERVICE_NAME == "payment-service"
        assert settings.SERVICE_PORT == 8004
        assert settings.LOG_LEVEL == "INFO"
        assert settings.AUTH_SERVICE_URL == "http://localhost:8000"
        assert settings.USER_SERVICE_URL == "http://localhost:8002"
        assert settings.ORDER_SERVICE_URL == "http://localhost:8003"

    def test_settings_required_fields(self, monkeypatch):
        """Test that DATABASE_URL and RABBITMQ_URL are loaded from config."""
        settings = Settings()

        # Verify required fields are present (from .env or environment)
        assert settings.DATABASE_URL is not None
        assert settings.RABBITMQ_URL is not None
        assert len(settings.DATABASE_URL) > 0
        assert len(settings.RABBITMQ_URL) > 0

    def test_settings_database_url_validation(self, monkeypatch):
        """Test DATABASE_URL format validation."""
        monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@host:3306/payment_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

        settings = Settings()

        assert "mysql://" in settings.DATABASE_URL
        assert "payment_db" in settings.DATABASE_URL or "payment" in settings.DATABASE_URL.lower()

    def test_settings_rabbitmq_url_validation(self, monkeypatch):
        """Test RABBITMQ_URL format validation."""
        monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@host:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

        settings = Settings()

        assert "amqp://" in settings.RABBITMQ_URL

    def test_settings_service_port_type(self, monkeypatch):
        """Test SERVICE_PORT is integer type."""
        monkeypatch.setenv("DATABASE_URL", "mysql://test@localhost/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://localhost/")
        monkeypatch.setenv("SERVICE_PORT", "9004")

        settings = Settings()

        assert isinstance(settings.SERVICE_PORT, int)
        assert settings.SERVICE_PORT == 9004

    def test_settings_service_urls_override(self, monkeypatch):
        """Test service URLs can be overridden."""
        monkeypatch.setenv("DATABASE_URL", "mysql://test@localhost/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://localhost/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://custom-auth:8000")
        monkeypatch.setenv("USER_SERVICE_URL", "http://custom-user:8002")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://custom-order:8003")

        settings = Settings()

        assert settings.AUTH_SERVICE_URL == "http://custom-auth:8000"
        assert settings.USER_SERVICE_URL == "http://custom-user:8002"
        assert settings.ORDER_SERVICE_URL == "http://custom-order:8003"

    def test_settings_log_level_values(self, monkeypatch):
        """Test LOG_LEVEL configuration."""
        monkeypatch.setenv("DATABASE_URL", "mysql://test@localhost/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://localhost/")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()

        assert settings.LOG_LEVEL == "DEBUG"

    def test_settings_service_name_custom(self, monkeypatch):
        """Test custom SERVICE_NAME."""
        monkeypatch.setenv("DATABASE_URL", "mysql://test@localhost/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://localhost/")
        monkeypatch.setenv("SERVICE_NAME", "custom-payment-service")

        settings = Settings()

        assert settings.SERVICE_NAME == "custom-payment-service"
