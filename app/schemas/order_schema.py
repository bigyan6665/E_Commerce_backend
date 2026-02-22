from pydantic import BaseModel, Field
from datetime import datetime


class OrderCreate(BaseModel):
    productid:int
    userid:int
    quantity:int = Field(gt=0)


class OrderItemResponse(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    model_config = {"from_attributes": True}

from app.schemas.customers_schema import CustomerBase
class OrderResponse(BaseModel):
    id:int
    user: CustomerBase
    items: list[OrderItemResponse]
    order_date: datetime
    total_amount: float
    model_config = {"from_attributes":True}
