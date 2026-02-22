from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationInfo
from datetime import datetime
from enum import Enum

class Roles(str,Enum):
    customer = "customer"
    admin = "admin"

# Base schema with common attributes
class SignupBase(BaseModel):
    name: str 
    address: str 
    email: EmailStr 
    contact: str = Field(min_length=10,max_length=10)
    password:str 
    confirm_password:str 
    is_active:bool = Field(default=True)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cla,cpass,info:ValidationInfo):
        if 'password' in info.data and info.data['password'] != cpass:
            raise ValueError("Passwords donot match")
        return cpass

class AdminCreate(SignupBase):
    admin_create_key:str

# Base schema with common attributes
class LoginBase(BaseModel):
    email: EmailStr 
    password:str 
