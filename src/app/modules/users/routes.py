from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.authentication import get_current_user
from app.infrastructure.database.session import get_db_session
from app.modules.users.controller import UserController
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead
from app.modules.users.service import UserService

router = APIRouter()

def get_user_controller(session: AsyncSession = Depends(get_db_session)) -> UserController:
    return UserController(UserService(UserRepository(session), session))

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)) -> UserRead:
    result = await controller.get_current_user(current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result
