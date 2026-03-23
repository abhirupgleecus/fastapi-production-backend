from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    #App
    APP_NAME: str = "FastAPI First App"
    DEBUG: bool = False

    #Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    #JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()