from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    admin_password: str = "7788"
    secret_key: str = "5"
    database_url: str = "sqlite:///./data/cards.db"
    token_expire_hours: int = 24
    model_config = ConfigDict(env_file="../.env", extra="ignore")

    # class Config:
    #     env_file = "../.env"
    #     extra = "ignore"

settings = Settings()
