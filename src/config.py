from pathlib import Path
from typing import ClassVar, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT.joinpath('.env')


# ---------------------------------------------------------------------------------------------
# Base Config
# ---------------------------------------------------------------------------------------------
class BaseConfigSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=['.env', str(ENV_FILE_PATH)],
        env_file_encoding='utf-8',
        extra='ignore',
        frozen=True,
        case_sensitive=False,
    )


# ---------------------------------------------------------------------------------------------
# Main Settings
# ---------------------------------------------------------------------------------------------
class Settings(BaseConfigSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
