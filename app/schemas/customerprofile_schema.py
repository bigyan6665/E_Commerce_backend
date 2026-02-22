from pydantic import BaseModel, Field
from enum import Enum

class CustomerProfileBase(BaseModel):
    loyalty_points: float
    is_verified: bool
    image_url:str | None
    image_public_id:str | None
    user_id: int

class CustomerProfileResponse(CustomerProfileBase):
    id : int
    model_config = {"from_attributes":True}

# inherits str and Enum
class Operation(str,Enum):
    add = "add"
    subtract = "subtract"

class LoyaltyPointsUpdate(BaseModel):
    points : float = Field(gt=0)
    operation : Operation

class VerificationUpdate(BaseModel):
    new_status : bool