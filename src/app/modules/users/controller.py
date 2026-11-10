from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

class UserController:
    """Adapts user use cases to public API schemas."""
    def __init__(self, service: UserService) -> None:
        self.service = service

    async def register(self, payload: UserCreate) -> UserRead:
        user = await self.service.register(str(payload.email), payload.password)
        return UserRead.model_validate(user)

    def get_current_user(self, user: User) -> UserRead:
        return UserRead.model_validate(user)
