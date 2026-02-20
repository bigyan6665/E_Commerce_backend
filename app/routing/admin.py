from fastapi import APIRouter, Depends, HTTPException,status
from app.helper import hashPassword
from app.schemas.apiresponse import APIResponse
from app.schemas.auth import SignupBase
from app.database.models import User
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.auth import AdminCreate
from app.config.app_config import getAppConfig

router = APIRouter(prefix="/admin")

# just for inserting an admin
@router.post("/add/",response_model=APIResponse)
def signup(admin:AdminCreate, db:Session = Depends(get_db)):
    """
    all users registered from this endpoint will have role = "admin"
    """
    conf = getAppConfig()
    if admin.admin_create_key != conf.ADMIN_CREATE_KEY:
        raise HTTPException(detail="Wrong key.",status_code=status.HTTP_401_UNAUTHORIZED)
    match_user = db.query(User).filter(User.email == admin.email).first()
    if match_user is not None:
        raise HTTPException(detail="User with this email is already registered",status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        user = User(
            name= admin.name,
            email = admin.email,
            address = admin.address,
            contact = admin.contact,
            password = hashPassword(admin.password),
            is_active = admin.is_active,
            created_date = admin.created_date,
            role = admin.role
            )
        db.add(user)
        db.commit()
        db.refresh(user)
    except:
        db.rollback()
        raise HTTPException(detail="Error while creating account",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Admin creation successful",success=True)