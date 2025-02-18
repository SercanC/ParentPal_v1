from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from .base import BaseService

class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, *, obj_in: UserCreate, user_id: str = None) -> User:
        """Create new user with hashed password"""
        db_obj = User(
            id=user_id,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            preferences=obj_in.preferences
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    async def update_last_sync(self, *, user_id: str, last_sync: datetime) -> User:
        """Update user's last sync timestamp"""
        user = await self.get(user_id)
        if user:
            user.last_sync = last_sync
            await self.db.commit()
            await self.db.refresh(user)
        return user