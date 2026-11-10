from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.exceptions import ConflictError
from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

class UserService:
    """User use cases; owns the transaction boundary."""
    def __init__(self, repository: UserRepository, session: AsyncSession) -> None:
        self.repository, self.session = repository, session
    async def register(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        if await self.repository.get_by_email(normalized):
            raise ConflictError("Email already registered")
        user = User(email=normalized, hashed_password=hash_password(password))
        try:
            await self.repository.add(user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Email already registered") from None
        return user
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_by_id(user_id)
