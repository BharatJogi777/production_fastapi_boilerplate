from app.modules.users.schemas import UserRead
from app.modules.users.service import UserService

class UserController:
    """Maps application results to public API schemas."""
    def __init__(self, service: UserService) -> None:
        self.service = service
    async def get_current_user(self, user_id: int) -> UserRead | None:
        user = await self.service.get_by_id(user_id)
        return UserRead.model_validate(user) if user else None
