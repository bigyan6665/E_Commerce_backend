from app.schemas.customerprofile_schema import Operation
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.products_schema import ProductAdd,ProductResponse
from app.database.models.product_models import Product
from app.schemas.apiresponse_schema import APIResponse
from app.database.models.product_models import Product
from app.schemas.products_schema import StockQuantityUpdate
from app.dependencies import PermissionChecker
from app.schemas.auth_schema import Roles

router = APIRouter(prefix="/products")

@router.get("/{productid}",response_model=APIResponse[ProductResponse],dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin,Roles.customer]))])
def get_product(productid:int,db:Session = Depends(get_db)):
    matched_prod = db.query(Product).filter(Product.id == productid).first()
    if matched_prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    return APIResponse(message="Product fetched successfully",success=True,content=matched_prod)

@router.post("/add/",response_model=APIResponse[ProductResponse],dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin]))])
def add_product(product:ProductAdd,db:Session = Depends(get_db)):
    try:
        prod = Product(**product.dict())
        db.add(prod)
        db.commit()
        db.refresh(prod)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{str(e)}")
    return APIResponse(message="Product added successfully",success=True,content=prod)

@router.put("/update_stock/{productid}",response_model=APIResponse[ProductResponse],dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin]))])
def update_stock(productid:int,data:StockQuantityUpdate,db:Session = Depends(get_db)):
    matched_prod = db.query(Product).filter(Product.id == productid).first()
    if matched_prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    try:
        if data.operation == Operation.add:
            matched_prod.stock_quantity = matched_prod.stock_quantity + data.update_quantity
        elif data.operation == Operation.subtract:
            if matched_prod.stock_quantity >= data.update_quantity:
                matched_prod.stock_quantity = matched_prod.stock_quantity - data.update_quantity
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Demand more than in stock")
        db.add(matched_prod)
        db.commit()
        db.refresh(matched_prod)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{str(e)}")
    return APIResponse(message=f"Stock quantity {data.operation.value}ed successfully",success=True,content=matched_prod)


@router.delete("/delete/{productid}",response_model=APIResponse[ProductResponse],dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin]))])
def delete_product(productid:int,db:Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == productid).first()
    if prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    try:
        db.delete(prod)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error in deleting product")
    return APIResponse(message="Product deleted successfully",success=True,content=prod)