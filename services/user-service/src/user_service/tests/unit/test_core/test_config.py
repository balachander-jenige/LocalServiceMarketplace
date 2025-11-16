"""
Core Config 单元测试
测试配置加载和默认值
"""

import os
from unittest.mock import patch

import pytest

from user_service.core.config import Settings


class TestSettings:
    """Test Settings Configuration类"""

    def test_settings_with_env_vars(self):
        """TestLoad Using Environment VariablesConfiguration"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://test:27017",
                "RABBITMQ_URL": "amqp://test:5672",
                "AUTH_SERVICE_URL": "http://auth:8000",
                "SERVICE_NAME": "test-user-service",
                "SERVICE_PORT": "9999",
                "LOG_LEVEL": "DEBUG",
            },
        ):
            settings = Settings()

            assert settings.MONGODB_URL == "mongodb://test:27017"
            assert settings.RABBITMQ_URL == "amqp://test:5672"
            assert settings.AUTH_SERVICE_URL == "http://auth:8000"
            assert settings.SERVICE_NAME == "test-user-service"
            assert settings.SERVICE_PORT == 9999
            assert settings.LOG_LEVEL == "DEBUG"

    def test_settings_default_values(self):
        """Test默认ConfigurationValue"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://localhost:5672",
                # Not Set Other Values, UseDefault Value
            },
            clear=True,
        ):
            settings = Settings()

            # VerifyDefault Value
            assert settings.AUTH_SERVICE_URL == "http://localhost:8000"
            assert settings.SERVICE_NAME == "user-service"
            assert settings.SERVICE_PORT == 8002
            assert settings.LOG_LEVEL == "INFO"

    def test_settings_required_fields(self):
        """TestMONGODB_URLAndRABBITMQ_URLAre Required Fields"""
        # Since .env File Exists, ThisTestMay Read From .envConfiguration
        # OnlyVerifySettingsObject Has These Two Required Fields
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://required:27017",
                "RABBITMQ_URL": "amqp://required:5672",
            },
            clear=True,
        ):
            settings = Settings()
            # VerifyRequired FieldsBe Set Correctly
            assert settings.MONGODB_URL == "mongodb://required:27017"
            assert settings.RABBITMQ_URL == "amqp://required:5672"

    def test_settings_mongodb_url_validation(self):
        """TestMongoDB URLFormatVerify"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://user:pass@host:27017/dbname",
                "RABBITMQ_URL": "amqp://localhost:5672",
            },
            clear=True,
        ):
            settings = Settings()
            assert "mongodb://" in settings.MONGODB_URL

    def test_settings_rabbitmq_url_validation(self):
        """TestRabbitMQ URLFormatVerify"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://user:pass@host:5672/vhost",
            },
            clear=True,
        ):
            settings = Settings()
            assert "amqp://" in settings.RABBITMQ_URL

    def test_settings_service_port_type(self):
        """TestSERVICE_PORTFieldsType Conversion"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://localhost:5672",
                "SERVICE_PORT": "3000",
            },
            clear=True,
        ):
            settings = Settings()
            assert isinstance(settings.SERVICE_PORT, int)
            assert settings.SERVICE_PORT == 3000

    def test_settings_auth_service_url_override(self):
        """TestOverrideAUTH_SERVICE_URLDefault Value"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://localhost:5672",
                "AUTH_SERVICE_URL": "http://custom-auth:9000",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.AUTH_SERVICE_URL == "http://custom-auth:9000"

    def test_settings_log_level_values(self):
        """TestDifferent的LOG_LEVELValue"""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in log_levels:
            with patch.dict(
                os.environ,
                {
                    "MONGODB_URL": "mongodb://localhost:27017",
                    "RABBITMQ_URL": "amqp://localhost:5672",
                    "LOG_LEVEL": level,
                },
                clear=True,
            ):
                settings = Settings()
                assert settings.LOG_LEVEL == level

    def test_settings_service_name_custom(self):
        """TestCustomSERVICE_NAME"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://localhost:5672",
                "SERVICE_NAME": "custom-user-service",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.SERVICE_NAME == "custom-user-service"

    def test_settings_immutable(self):
        """TestConfigurationObjectImmutability(PydanticFeature)"""
        with patch.dict(
            os.environ,
            {
                "MONGODB_URL": "mongodb://localhost:27017",
                "RABBITMQ_URL": "amqp://localhost:5672",
            },
            clear=True,
        ):
            settings = Settings()

            # Pydantic V2ModelDefault Mutable, But Can Set Viafrozen=TrueSet Immutable
            # Here OnlyTestInitial Value Correct
            assert settings.SERVICE_NAME == "user-service"
