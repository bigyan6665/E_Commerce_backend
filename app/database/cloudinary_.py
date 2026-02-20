import cloudinary
from app.config.app_config import getAppConfig

conf = getAppConfig()

cloudinary.config(
    cloud_name = conf.CLOUDINARY_CLOUD_NAME,
    api_key = conf.CLOUDINARY_API_KEY,
    api_secret = conf.CLOUDINARY_API_SECRET
)