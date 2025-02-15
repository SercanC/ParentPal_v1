from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.services.factory import ServiceFactory
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_services(db: Annotated[AsyncSession, Depends(get_db)]) -> ServiceFactory:
    """Dependency for getting service factory"""
    return ServiceFactory(db)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> User:
    """Dependency for getting current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await services.user.get(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Dependency for getting current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user