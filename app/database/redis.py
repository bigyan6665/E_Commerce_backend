import redis
from app.config.app_config import getAppConfig

config = getAppConfig()

redis_client = redis.Redis(
    host=config.redis_host,
    port=config.redis_port,
    decode_responses=True,
    username=config.redis_db_username,
    password=config.redis_db_password,
)
