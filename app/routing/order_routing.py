from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models.product_models import Product
from app.schemas.apiresponse_schema import APIResponse
from app.schemas.order_schema import OrderCreate,OrderResponse
from app.database.models.order_models import Order,OrderItem
from app.database.models.user_models import User
from app.dependencies import PermissionChecker
from app.schemas.auth_schema import Roles

router = APIRouter(prefix="/order")

@router.post("/add/",response_model=APIResponse[OrderResponse],dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.customer]))])
def place_order(user_order:OrderCreate,db:Session = Depends(get_db)):
    matched_prod = db.query(Product).filter(Product.id == user_order.productid).first()
    if matched_prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    user = db.query(User).filter((User.id == user_order.userid)&(User.role == Roles.customer)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
    
    if matched_prod.stock_quantity >= user_order.quantity:
        try:
            # method1
            order = Order(
                total_amount = user_order.quantity * matched_prod.price,
                # user_id = user_order.userid, # back populating User table
                user = user
            )
            order.items.append(OrderItem(
                    product_id = user_order.productid ,
                    quantity = user_order.quantity
                ))
            matched_prod.stock_quantity = matched_prod.stock_quantity - user_order.quantity
            db.add(order)
            db.commit()
            db.refresh(order)
            db.refresh(matched_prod)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Demand more than in stock")
    return APIResponse(message="Order placed successfully",success=True,content=order)

# admin can delete any customer's order
# customers can delete own orders only
@router.delete("/delete/",response_model=APIResponse)
def delete_order(order_id:int,db:Session = Depends(get_db),current_user:dict = Depends(PermissionChecker(allowed_roles=[Roles.customer,Roles.admin]))):
    matched_order = db.query(Order).filter(Order.id == order_id).first()
    if matched_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
    
    if current_user.get("role") != Roles.admin and matched_order.user_id != current_user.get("id"):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Permission denied") 
    
    try:
        db.delete(matched_order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    return APIResponse(message="Order deleted successfully",success=True)