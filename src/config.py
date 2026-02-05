from pathlib import Path
from typing import ClassVar, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT.joinpath('.env')


class BaseConfigSettings(BaseSettings):
    """Переменные окружения приложения."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=['.env', str(ENV_FILE_PATH)],
        env_file_encoding='utf8',
        extra='ignore',
        frozen=True,
        case_sensitive=False,
    )


class Settings(BaseConfigSettings):
    """Настройки приложения."""

    api_debug: bool
    api_version: str
    api_environment: Literal['development', 'staging', 'production']
    api_service_name: str
    api_secret_key: str
    api_access_token_expire_minutes: int | float
    api_refresh_token_expire_days: int
    api_jwt_encode_algorithm: str

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    postgres_echo_sql: bool


def get_settings() -> Settings:
    """Получение настроек на основании переменных окружения."""
    return Settings()
