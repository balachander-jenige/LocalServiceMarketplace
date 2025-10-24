"""Tests for review service configuration."""

import pytest
from pydantic import ValidationError

from review_service.core.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_with_env_vars(self, monkeypatch):
        """Test settings load from environment variables."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")

        settings = Settings()

        assert settings.MONGODB_URL == "mongodb://localhost:27017/test"
        assert settings.RABBITMQ_URL == "amqp://guest:guest@localhost:5672/"
        assert settings.AUTH_SERVICE_URL == "http://localhost:8000"
        assert settings.ORDER_SERVICE_URL == "http://localhost:8003"
        assert settings.USER_SERVICE_URL == "http://localhost:8002"

    def test_settings_default_values(self, monkeypatch):
        """Test default values for optional settings."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")

        settings = Settings()

        assert settings.SERVICE_NAME == "review-service"
        assert settings.SERVICE_PORT == 8005
        assert settings.LOG_LEVEL == "INFO"

    def test_settings_required_fields(self, monkeypatch):
        """Test that required fields raise ValidationError when missing."""
        # Clear all environment variables
        for key in ["MONGODB_URL", "RABBITMQ_URL", "AUTH_SERVICE_URL", "ORDER_SERVICE_URL", "USER_SERVICE_URL"]:
            monkeypatch.delenv(key, raising=False)

        # Ensure .env file is not read
        monkeypatch.setenv("SETTINGS_ENV_FILE", "/nonexistent/.env")

        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        assert "MONGODB_URL" in required_fields
        assert "RABBITMQ_URL" in required_fields

    def test_settings_mongodb_url_validation(self, monkeypatch):
        """Test MongoDB URL format."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://user:pass@localhost:27017/review_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")

        settings = Settings()
        assert settings.MONGODB_URL.startswith("mongodb://")
        assert "review_db" in settings.MONGODB_URL

    def test_settings_rabbitmq_url_validation(self, monkeypatch):
        """Test RabbitMQ URL format."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/vhost")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")

        settings = Settings()
        assert settings.RABBITMQ_URL.startswith("amqp://")
        assert "vhost" in settings.RABBITMQ_URL

    def test_settings_service_port_type(self, monkeypatch):
        """Test service port is integer."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")
        monkeypatch.setenv("SERVICE_PORT", "9005")

        settings = Settings()
        assert isinstance(settings.SERVICE_PORT, int)
        assert settings.SERVICE_PORT == 9005

    def test_settings_service_urls_override(self, monkeypatch):
        """Test service URLs can be overridden."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://auth:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://order:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://user:8002")

        settings = Settings()
        assert settings.AUTH_SERVICE_URL == "http://auth:8000"
        assert settings.ORDER_SERVICE_URL == "http://order:8003"
        assert settings.USER_SERVICE_URL == "http://user:8002"

    def test_settings_log_level_values(self, monkeypatch):
        """Test log level can be set."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()
        assert settings.LOG_LEVEL == "DEBUG"

    def test_settings_service_name_custom(self, monkeypatch):
        """Test service name can be customized."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017/test")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        monkeypatch.setenv("AUTH_SERVICE_URL", "http://localhost:8000")
        monkeypatch.setenv("ORDER_SERVICE_URL", "http://localhost:8003")
        monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8002")
        monkeypatch.setenv("SERVICE_NAME", "custom-review-service")

        settings = Settings()
        assert settings.SERVICE_NAME == "custom-review-service"
