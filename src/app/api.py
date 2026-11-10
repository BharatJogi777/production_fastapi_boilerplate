import jwt
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import decode_token
from app.db import get_db_session
from app.domain import AuthService, Token, User, UserCreate, UserRead, UserRepository

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
logger = structlog.get_logger()

async def current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_session)) -> User:
    unauthorized = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id = int(decode_token(token).get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise unauthorized from None
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user

@router.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "alive"}

@router.get("/health/ready", tags=["health"])
async def readiness(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "ready"}

@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> UserRead:
    user = await AuthService(UserRepository(session)).register(str(payload.email), payload.password)
    return UserRead.model_validate(user)

@router.post("/auth/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db_session)) -> Token:
    token = await AuthService(UserRepository(session)).authenticate(form.username, form.password)
    return Token(access_token=token)

@router.get("/users/me", response_model=UserRead)
async def me(user: User = Depends(current_user)) -> UserRead:
    return UserRead.model_validate(user)
