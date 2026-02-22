from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas import customers_schema 
from app.database.models.user_models import User
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.dependencies import authenticate_user,PermissionChecker,check_roles
from app.schemas.auth_schema import Roles
from app.helper import delete_image, del_cloudinary_dir
from app.schemas.apiresponse_schema import APIResponse

router = APIRouter(prefix="/customers")
# router = APIRouter(prefix="/customers",dependencies=[Depends(check_roles([Roles.admin)])])
# all the following routes will get "/customers" prefix
# all the following routes will be guarded by check_rules(). admin only can access these routes

# userid in .get() captures the url parameters

# admin can get any customers' details
# customers can get own details only
@router.get("/{userid}",response_model=APIResponse[customers_schema.CustomerResponse])
def get_customer(userid: int, db: Session = Depends(get_db),current_user:dict = Depends(PermissionChecker(allowed_roles=[Roles.admin,Roles.customer]))):
    # fetch customers only not admin
    cust = db.query(User).filter((User.id == userid)&(User.role == Roles.customer)).first()
    if cust is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
    
    if current_user.get("role") != Roles.admin and cust.id != current_user.get("id"):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Permission denied") 
    
    return APIResponse(message="Customer fetched successfully",success=True,content=cust)

# admin can delete any customers' account
# customers can delete own account only
@router.delete("/delete/{userid}",response_model=APIResponse)
def delete_customer(userid:int,db:Session = Depends(get_db),current_user:dict = Depends(PermissionChecker(allowed_roles=[Roles.admin,Roles.customer]))):
    # delete customers not admin
    cust = db.query(User).filter((User.id == userid)&(User.role == Roles.customer)).first()
    if cust is None:
        raise HTTPException(detail="Customer not found",status_code=status.HTTP_404_NOT_FOUND)
    
    if current_user.get("role") != Roles.admin and cust.id != current_user.get("id"):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Permission denied")  

    try:
        db.delete(cust)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(detail="Error in deleting customer",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    del_cloudinary_dir(dir_path=f"customers_profiles/id{userid}") # cleaning iamges folder from cloudinary
    return APIResponse(message=f"Customer deleted successfully",success=True)

# admin can edit any customers' account
# customers can edit own account only
@router.put("/update/{userid}",response_model=APIResponse)
def update_customer(userid:int,item:customers_schema.CustomerUpdate,db:Session = Depends(get_db),current_user:dict = Depends(PermissionChecker(allowed_roles=[Roles.admin,Roles.customer]))):
    # update customer only not admin
    cust = db.query(User).filter((User.id == userid) & (User.role == Roles.customer)).first()
    if cust is None:
       raise HTTPException(detail="Customer not found",status_code=status.HTTP_404_NOT_FOUND)

    if current_user.get("role") != Roles.admin and cust.id != current_user.get("id"):
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Permission denied")  

    try :
        cust.address = item.address
        cust.contact = item.contact
        cust.email = item.email
        cust.name = item.name
        db.commit()
        db.refresh(cust)
    except Exception as e:
        db.rollback()
        raise HTTPException(detail=f"Error in updating customer details:{str(e)}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Customer details updated successfully",success=True)