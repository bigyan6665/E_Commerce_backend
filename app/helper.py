from pwdlib import PasswordHash
import jwt
from app.config.app_config import getAppConfig
from datetime import datetime,timezone,timedelta
from uuid import uuid4
from app.database.redis import redis_client
from app.database import cloudinary_ # triggers cloudinary.config and thus cloudinary.upload() can work
import cloudinary.uploader
import cloudinary.api
import cloudinary.exceptions
from fastapi import UploadFile

def hashPassword(password:str)->str:
    password_hasher = PasswordHash.recommended()
    return password_hasher.hash(password)

def verifyPassword(password:str,hashed_password:str)->bool:
    password_hasher = PasswordHash.recommended()
    return password_hasher.verify(password,hashed_password)   

def createAccessToken(data:dict)->str:
    config = getAppConfig()
    payload = data.copy()

    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    payload.update({
        "exp":expiry_time, # expiry timestamp for each access token
        "jti":str(uuid4()) # unique token id for each access token
        })

    token = jwt.encode(payload,config.secret_key,algorithm=config.algorithm)
    return token


def decodeAccessToken(token:str)->dict:
    config = getAppConfig()
    payload = jwt.decode(token,config.secret_key,algorithms=[config.algorithm])
    return payload


def blacklist_token(jti:str,exp_timestamp:int):
    key = f"Blacklisted with JTI = {jti}"
    ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        redis_client.set(name=key,value="1",ex=ttl)

def is_token_blacklisted(jti:str)->int:
    """"
    Return:
        1 if exists else 0
    """
    key = f"Blacklisted with JTI = {jti}"
    return redis_client.exists(key)
    

def upload_image(image:UploadFile,folder:str)->dict:
    res = cloudinary.uploader.upload(
        image.file,
        folder = folder,
        resource_type = "image"
    )
    return {
        "url":res["secure_url"],
        "public_id":res["public_id"]
    }

def delete_image(public_id:str):
    res = cloudinary.uploader.destroy(public_id=public_id)

# If asset's public_id = users/123/profile.jpg
# users/123 is the folder_path inside which profile.jpg lies
# Thus, prefix of public id = folder_path
def del_cloudinary_dir(dir_path:str):
    try:
        # first delete folder content 
        cloudinary.api.delete_resources_by_prefix(dir_path) # doesnot raise error if asset not found
        # then only delete the folder 
        cloudinary.api.delete_folder(dir_path) # raises cloudinary.exceptions.NotFound error when folder not found
        # cannot delete folder if assets are present
    except cloudinary.exceptions.NotFound:
        pass # do nothing if folder is absent