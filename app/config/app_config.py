from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache # Least Recently Used (LRU) cache

class AppConfig(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes:int
    redis_host : str
    redis_port : int
    redis_db_username : str
    redis_db_password : str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    ADMIN_CREATE_KEY : str
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache # When the same inputs occur again, it returns the cached result instead of recomputing, significantly improving speed.
def getAppConfig():# this method gives appconfig obj whenever called
    return AppConfig()