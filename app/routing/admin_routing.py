from fastapi import APIRouter, Depends, HTTPException,status
from app.helper import hashPassword
from app.schemas.apiresponse_schema import APIResponse
from app.database.models.user_models import User
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.auth_schema import AdminCreate
from app.config.app_config import getAppConfig
from app.schemas.auth_schema import Roles

router = APIRouter(prefix="/admin")

# just for inserting an admin
@router.post("/add/",response_model=APIResponse)
def add_admin(admin:AdminCreate, db:Session = Depends(get_db)):
    """
    all users registered from this endpoint will have role = "admin"
    """
    conf = getAppConfig()
    if admin.admin_create_key != conf.ADMIN_CREATE_KEY:
        raise HTTPException(detail="Wrong key.",status_code=status.HTTP_401_UNAUTHORIZED)
    
    match_user = db.query(User).filter((User.email == admin.email)|(User.contact == admin.contact)).first()
    if match_user is not None:
        raise HTTPException(detail="User with this email or contact no. is already registered",status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        user = User(
            name= admin.name,
            email = admin.email,
            address = admin.address,
            contact = admin.contact,
            password = hashPassword(admin.password),
            is_active = admin.is_active,
            role = Roles.admin
            )
        db.add(user)
        db.commit()
        db.refresh(user)
    except:
        db.rollback()
        raise HTTPException(detail="Error while creating account",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Admin creation successful",success=True)