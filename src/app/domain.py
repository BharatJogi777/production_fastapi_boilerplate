from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from fastapi import HTTPException, status
from app.db import Base
from app.core import create_token, hash_password, verify_password

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)
    async def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, hashed_password=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    async def list(self, offset: int, limit: int) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.id).offset(offset).limit(limit))
        return list(result.scalars().all())

class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users
    async def register(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        if await self.users.get_by_email(normalized):
            raise HTTPException(status_code=409, detail="Email already registered")
        return await self.users.create(normalized, hash_password(password))
    async def authenticate(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email.strip().lower())
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive account")
        return create_token(str(user.id))
