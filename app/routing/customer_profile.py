from app.schemas.customerprofile import LoyaltyPointsUpdate, Operation, VerificationUpdate, CustomerProfileResponse
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException,status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.dependencies import authenticate_user,PermissionChecker,check_roles
from app.helper import upload_image
from pathlib import Path
from app.helper import delete_image
from app.schemas.auth import Roles
from app.database.models import CustomerProfile
from app.schemas.apiresponse import APIResponse

# router = APIRouter(prefix="/customer_profile",dependencies=[Depends(check_roles([Roles.admin,Roles.customer]))])
router = APIRouter(prefix="/customer_profile",dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.admin,Roles.customer]))])
# all the following routes will get "/customers" prefix
# all the following routes will be guarded by check_rules(). all type of users can access these routes

@router.put("/update_profile_picture/{userid}",response_model=APIResponse[dict])
def update_profile_picture(userid:int,image:UploadFile = File(...),db:Session = Depends(get_db)):
    # validating file types
    ALLOWED_TYPES = [".jpeg",".jpg", ".png", ".webp"]
    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(detail="File type not supported",status_code=status.HTTP_406_NOT_ACCEPTABLE)
   
    # uploading image url and public id to db
    matched_profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == userid).first()
    if matched_profile is not None:
        # cloudinary ma euta customer ko sabai images basxa
        # tara db ma chai recently uploaded image ko matra url,public id basxa
        # uploading images to cloudinary
        try:
            res = upload_image(image=image,folder=f"customers_profiles/id{userid}") 
        except Exception as e:
            raise HTTPException(detail=f"Error while uploading image to cloudinary{str(e)}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # update profile
            matched_profile.image_url = res["url"]
            matched_profile.image_public_id = res["public_id"]
            db.commit()
            db.refresh(matched_profile)
        except Exception as e:
            db.rollback()
            delete_image(public_id=res["public_id"])
            raise HTTPException(detail=f"Error while uploading image url to db:{str(e)}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return APIResponse(message=f"Profile image with customer_id:{userid} updated successfully",success=True,content=res)
    else:
        raise HTTPException(detail=f"Customer profile not found",status_code=status.HTTP_404_NOT_FOUND)
    

@router.get("/{userid}",response_model=APIResponse[CustomerProfileResponse])
def get_profile(userid:int,db:Session = Depends(get_db)):
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == userid).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer profile not found") 
    return APIResponse(message="Customer profile fetched succesfully",success=True,content=profile)

@router.put("/update_loyalty_points/{userid}",response_model=APIResponse[CustomerProfileResponse])
def update_loyalty_points(userid:int,data:LoyaltyPointsUpdate,db:Session = Depends(get_db)):
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == userid).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer profile not found") 
    try:
        if data.operation == Operation.add:
            profile.loyalty_points = profile.loyalty_points + data.points
        elif data.operation == Operation.subtract:
            profile.loyalty_points = profile.loyalty_points - data.points
        db.commit()
        db.refresh(profile)
    except:
        db.rollback()
        raise HTTPException(detail=f"Error in updating loyalty points",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Loyalty point updated successfully",success=True,content=profile)

@router.put("/update_verification_status/{userid}",response_model=APIResponse[CustomerProfileResponse])
def update_verification_status(userid:int,data:VerificationUpdate,db:Session = Depends(get_db)):
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == userid).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Customer profile not found") 
    try:
        profile.is_verified = data.new_status
        db.commit()
        db.refresh(profile)
    except:
        db.rollback()
        raise HTTPException(detail=f"Error in updating verification status",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Verification status updated successfully",success=True,content=profile)