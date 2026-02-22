from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.auth_schema import SignupBase,LoginBase
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models.user_models import User
from app.helper import hashPassword,verifyPassword, createAccessToken, blacklist_token,decodeAccessToken,is_token_blacklisted
from app.dependencies import oauth2_schema
from app.schemas.apiresponse_schema import APIResponse
from app.database.models.user_models import CustomerProfile
from app.dependencies import PermissionChecker
from app.schemas.auth_schema import Roles

router = APIRouter(prefix="/auth")

@router.post("/signup/",response_model=APIResponse)
def signup(signupDetails:SignupBase, db:Session = Depends(get_db)):
    """
    all users registered from this endpoint will have role = "customer"
    """
    match_user = db.query(User).filter((User.email == signupDetails.email)|(User.contact == signupDetails.contact)).first()
    if match_user is not None:
        raise HTTPException(detail="User with this email or contact no. is already registered",status_code=status.HTTP_303_SEE_OTHER)
    try:
        user = User(
            name= signupDetails.name,
            email = signupDetails.email,
            address = signupDetails.address,
            contact = signupDetails.contact,
            password = hashPassword(signupDetails.password),
            is_active = signupDetails.is_active
            )
        user.customer_profile = CustomerProfile()
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(detail=f"Error while creating account:{str(e)}",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIResponse(message="Signup successful",success=True)

@router.post("/login/",response_model=APIResponse[dict])
def login(loginDetails:LoginBase,db:Session= Depends(get_db)):
    user = db.query(User).filter(User.email == loginDetails.email).first()
    if user is None:
        raise HTTPException(detail="The email is not registered",status_code=status.HTTP_404_NOT_FOUND)
    verified = verifyPassword(hashed_password=user.password,password=loginDetails.password)
    if not verified:
        raise HTTPException(detail="Please enter correct password",status_code=status.HTTP_403_FORBIDDEN)
    payload = {
        "id": user.id,
        "name":user.name,
        "email":user.email,
        "role":user.role
    }
    access_token = createAccessToken(data=payload)
    payload['access_token'] = access_token
    return APIResponse(message="Logged in successfully",success=True,content=payload)

@router.post("/logout/",response_model=APIResponse,dependencies=[Depends(PermissionChecker(allowed_roles=[Roles.customer]))])
def logout(token:str = Depends(oauth2_schema)):
    try:
        payload = decodeAccessToken(token=token)
        jti = payload.get('jti')
        if is_token_blacklisted(jti=jti) != 1:
            exp_timestamp = payload.get("exp")
            blacklist_token(jti=jti,exp_timestamp=exp_timestamp)
            return APIResponse(message="Logged out successfully",success=True)
        return APIResponse(message="Already logged out",success=True)
    except Exception:
        raise HTTPException(detail="Unauthorized token",status_code=status.HTTP_401_UNAUTHORIZED)