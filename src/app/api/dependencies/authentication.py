import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_access_token
from app.infrastructure.database.session import get_db_session
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_db_session)) -> User:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    try:
        claims = decode_access_token(token)
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise error from None
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise error
    return user
