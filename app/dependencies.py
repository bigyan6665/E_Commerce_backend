from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from app.helper import decodeAccessToken
from app.helper import is_token_blacklisted
import jwt
from typing import List

# oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/auth/login")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login/") # tokenUrl = route of login where token is created
# OAuth2PasswordBearer tells FastAPI to Expect token from Authorization header using Bearer scheme(Bearer <jwt>).And extracts 
# token from the header automatically and passed to following fn:

def authenticate_user(token:str = Depends(oauth2_schema)):
    try:
        payload = decodeAccessToken(token)
        jti = payload.get("jti")
        if is_token_blacklisted(jti=jti) == 1: # the token is blacklisted but have not passed expiry time
            raise
        # print(payload)
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Unauthorized token",headers={"Authorization":"Bearer"})

# using closure as dependency
def check_roles(allowed_roles:list[str]):# closure style nested dependency
    def auth(payload:dict = Depends(authenticate_user)):
        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"{role} are not allowed in this route")
    return auth

# using class as dependency
# works same as check_roles
class PermissionChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(oauth2_schema)) -> None:
        try:
            payload = decodeAccessToken(token) # token authentication
            jti = payload.get("jti")
            if is_token_blacklisted(jti=jti) == 1: # the token is blacklisted but have not passed expiry time
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Unauthorized token"
                )
            role = payload.get("role")
            if role not in self.allowed_roles: #RBAC
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"'{role}' not allowed in this route"
                )
        except (jwt.ExpiredSignatureError,jwt.DecodeError): # catch multiple exceptions
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized token")
        except Exception: # catches other exceptions and propagates it
            raise 