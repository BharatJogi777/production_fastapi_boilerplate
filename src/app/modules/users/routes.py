from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.authentication import get_current_user
from app.infrastructure.database.session import get_db_session
from app.modules.users.controller import UserController
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

router = APIRouter()

def get_user_controller(session: AsyncSession = Depends(get_db_session)) -> UserController:
    return UserController(UserService(UserRepository(session), session))

@router.post("", response_model=UserRead, status_code=201)
async def register_user(payload: UserCreate,
    controller: UserController = Depends(get_user_controller)) -> UserRead:
    return await controller.register(payload)

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)) -> UserRead:
    return controller.get_current_user(current_user)
