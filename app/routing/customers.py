from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas import customers 
from app.database import models
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.dependencies import authenticate_user,PermissionChecker,check_roles
from app.schemas.auth import Roles
from app.helper import delete_image, del_cloudinary_dir
from app.schemas.apiresponse import APIResponse

router = APIRouter(prefix="/customers",dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin]))])
# router = APIRouter(prefix="/customers",dependencies=[Depends(check_roles([Roles.admin)])])
# all the following routes will get "/customers" prefix
# all the following routes will be guarded by check_rules(). admin only can access these routes

# customerid in .get() captures the url parameters
@router.get("/{userid}",response_model=APIResponse[customers.CustomerResponse])
def get_customer(userid: int, db: Session = Depends(get_db)):
    # fetch customers only not admin
    cust = db.query(models.User).filter((models.User.id == userid)&(models.User.role == Roles.customer)).first()
    if cust is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer not found")
    return APIResponse(message="Customer fetched successfully",success=True,content=cust)

@router.delete("/delete/{userid}",response_model=APIResponse)
def delete_customer(userid:int,db:Session = Depends(get_db)):
    # delete customers not admin
    cust = db.query(models.User).filter((models.User.id == userid)&(models.User.role == Roles.customer)).first()
    if cust is None:
        raise HTTPException(detail="Customer not found",status_code=status.HTTP_404_NOT_FOUND)
    try:
        db.delete(cust)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(detail="Error in deleting customer",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    del_cloudinary_dir(dir_path=f"customers_profiles/id{userid}") # cleaning iamges folder from cloudinary
    return APIResponse(message=f"Customer deleted successfully",success=True)

@router.put("/update/{userid}",response_model=APIResponse)
def update_customer(userid:int,item:customers.CustomerUpdate,db:Session = Depends(get_db)):
    # update customer only not admin
    cust = db.query(models.User).filter((models.User.id == userid) & (models.User.role == Roles.customer)).first()
    if cust is None:
       raise HTTPException(detail="Customer not found",status_code=status.HTTP_404_NOT_FOUND)
    # email_matched = db.query(models.User).filter(models.User.email == item.email).first()
    # if email_matched is not None:
    #     raise HTTPException(detail="The email is already registered",status_code=status.HTTP_303_SEE_OTHER)
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