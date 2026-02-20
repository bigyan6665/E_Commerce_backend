from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Base schema with common attributes
class CustomerBase(BaseModel):
    name: str 
    address:str 
    email: EmailStr 
    contact:str = Field(min_length=10,max_length=10)
    is_active:bool
    created_date:datetime
    role:str


class CustomerUpdate(BaseModel):
    # only following features
    name: str 
    address:str 
    email: EmailStr 
    contact:str = Field(min_length=10,max_length=10)

class CustomerResponse(CustomerBase):
    # all features of CustomerBase + following
    id : int
    password: str
    model_config = {"from_attributes":True}

