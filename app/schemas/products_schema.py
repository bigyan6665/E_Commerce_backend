from pydantic import BaseModel
from app.schemas.customerprofile_schema import Operation

class ProductBase(BaseModel):
    name:str
    price:float
    description: str
    stock_quantity: int


class ProductAdd(ProductBase):
    pass

class ProductResponse(ProductBase):
    id:int
    model_config = {"from_attributes":True}

class StockQuantityUpdate(BaseModel):
    update_quantity:int
    operation: Operation