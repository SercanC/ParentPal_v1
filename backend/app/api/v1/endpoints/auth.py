from datetime import timedelta
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash
)
from app.core.config import settings
from app.schemas.auth import Token, Login, RefreshToken
from app.schemas.user import UserCreate, User, UserWithToken, UserInDB
from app.api.deps import get_services
from app.services.factory import ServiceFactory
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/register", response_model=UserWithToken)
async def register(
    user_in: UserCreate,
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> UserWithToken:
    """Register a new user"""
    # Check if passwords match
    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user with this email already exists
    existing_user = await services.user.get_by_email(email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Generate UUID and create base user data
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "is_active": True,
        "preferences": user_in.preferences or {},
        "hashed_password": get_password_hash(user_in.password)
    }
    
    # Create user
    user = await services.user.create(user_data)
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # Convert SQLAlchemy model to dictionary and add tokens
    user_data = jsonable_encoder(user)
    return UserWithToken(
        **user_data,
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await services.user.get_by_email(email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    login_data: Login,
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> Token:
    """Login with email and password"""
    user = await services.user.get_by_email(email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    refresh_token: RefreshToken,
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> Token:
    """Get a new access token using refresh token"""
    try:
        payload = jwt.decode(
            refresh_token.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = await services.user.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )