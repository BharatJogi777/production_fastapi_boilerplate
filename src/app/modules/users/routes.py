from fastapi import APIRouter, Depends
from app.api.dependencies.authentication import get_current_user
from app.modules.users.controller import UserController
from app.modules.users.dependencies import get_user_controller
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)) -> UserRead:
    return controller.get_current_user(current_user)
