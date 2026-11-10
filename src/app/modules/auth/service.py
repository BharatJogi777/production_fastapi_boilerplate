from sqlalchemy.ext.asyncio import AsyncSession
from app.common.exceptions import AuthenticationError, ForbiddenError
from app.core.security import create_access_token, verify_password
from app.modules.users.repository import UserRepository

class AuthService:
    """Authentication use cases; delegates user persistence."""
    def __init__(self, users: UserRepository, session: AsyncSession) -> None:
        self.users, self.session = users, session
    async def authenticate(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email.strip().lower())
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError()
        if not user.is_active:
            raise ForbiddenError()
        return create_access_token(str(user.id))
