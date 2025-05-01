from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import ClassVar


class Settings(BaseSettings):
    DB_HOST: str = Field(env="DB_HOST")
    DB_NAME: str = Field(env="DB_NAME")
    DB_USER: str = Field(env="DB_USER")
    DB_PASS: str = Field(env="DB_PASS")
    DB_PORT: int = Field(env="DB_PORT")
    
    SECRET_KEY: ClassVar[str] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    REFRESH_SECRET_KEY: ClassVar[str] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    ALGORITHM : str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    RESET_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")

    @property
    def DATABASE_URL_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()