from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import ClassVar
import ssl

class Settings(BaseSettings):
    DB_HOST: str = Field(env="DB_HOST")
    DB_NAME: str = Field(env="DB_NAME")
    DB_USER: str = Field(env="DB_USER")
    DB_PASS: str = Field(env="DB_PASS")
    DB_PORT: int = Field(env="DB_PORT")
    
    ACCESS_SECRET_KEY: ClassVar[str] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    REFRESH_SECRET_KEY: ClassVar[str] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(..., env="EMAIL_FROM_NAME")
    USE_TLS: bool = Field(..., env="USE_TLS")
    START_TLS: bool = Field(..., env="START_TLS")

    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    APP_PORT: int = Field(..., env="APP_PORT")
    APP_HOST: str = Field(..., env="APP_HOST")

    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    BACKEND_URL: str = Field(..., env="BACKEND_URL")

    @property
    def DATABASE_URL_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def ssl_context(self):
        context = ssl.create_default_context()
        return context

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()