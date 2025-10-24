"""Tests for Order Service configuration."""

import pytest
from pydantic import ValidationError

from order_service.core.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_with_env_vars(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/test_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://auth:8000")
        monkeypatch.setenv("USER_SERVICE_URL", "http://user:8002")
        monkeypatch.setenv("SERVICE_NAME", "custom-order-service")
        monkeypatch.setenv("SERVICE_PORT", "9003")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()

        assert settings.DATABASE_URL == "mysql+aiomysql://test:test@localhost:3306/test_db"
        assert settings.RABBITMQ_URL == "amqp://guest:guest@localhost:5672/"
        assert settings.AUTH_SERVICE_URL == "http://auth:8000"
        assert settings.USER_SERVICE_URL == "http://user:8002"
        assert settings.SERVICE_NAME == "custom-order-service"
        assert settings.SERVICE_PORT == 9003
        assert settings.LOG_LEVEL == "DEBUG"

    def test_settings_default_values(self, monkeypatch):
        """Test default configuration values."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/order_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

        settings = Settings()

        assert settings.SERVICE_NAME == "order-service"
        assert settings.SERVICE_PORT == 8003
        assert settings.LOG_LEVEL == "INFO"
        assert settings.AUTH_SERVICE_URL == "http://localhost:8000"
        assert settings.USER_SERVICE_URL == "http://localhost:8002"

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
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

        settings = Settings()

        assert settings.DATABASE_URL.startswith("mysql+aiomysql://")
        assert "localhost:3306" in settings.DATABASE_URL

    def test_settings_rabbitmq_url_validation(self, monkeypatch):
        """Test RABBITMQ_URL format validation."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/vhost")

        settings = Settings()

        assert settings.RABBITMQ_URL.startswith("amqp://")
        assert "rabbitmq:5672" in settings.RABBITMQ_URL

    def test_settings_service_port_type(self, monkeypatch):
        """Test SERVICE_PORT is integer type."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("SERVICE_PORT", "9999")

        settings = Settings()

        assert isinstance(settings.SERVICE_PORT, int)
        assert settings.SERVICE_PORT == 9999

    def test_settings_service_urls_override(self, monkeypatch):
        """Test overriding service URLs."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://custom-auth:9000")
        monkeypatch.setenv("USER_SERVICE_URL", "http://custom-user:9002")

        settings = Settings()

        assert settings.AUTH_SERVICE_URL == "http://custom-auth:9000"
        assert settings.USER_SERVICE_URL == "http://custom-user:9002"

    def test_settings_log_level_values(self, monkeypatch):
        """Test LOG_LEVEL configuration."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")

        settings = Settings()

        assert settings.LOG_LEVEL == "WARNING"

    def test_settings_service_name_custom(self, monkeypatch):
        """Test custom SERVICE_NAME."""
        monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("SERVICE_NAME", "my-order-service")

        settings = Settings()

        assert settings.SERVICE_NAME == "my-order-service"
