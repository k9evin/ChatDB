from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # MySQL Configuration
    mysql_connection_string: str
    mysql_default_db: str

    # MongoDB Configuration
    mongo_connection_string: str
    mongo_default_db: str

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # Security
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> list[str]:
        return self.cors_origins.split(",")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
