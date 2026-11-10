from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db_session
from app.modules.auth.controller import AuthController
from app.modules.auth.schemas import TokenResponse
from app.modules.auth.service import AuthService
from app.modules.users.controller import UserController
from app.modules.users.dependencies import get_user_controller
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead

router = APIRouter()

def get_auth_controller(session: AsyncSession = Depends(get_db_session)) -> AuthController:
    return AuthController(AuthService(UserRepository(session), session))

@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate,
    controller: UserController = Depends(get_user_controller)) -> UserRead:
    return await controller.register(payload)

@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller)) -> TokenResponse:
    return await controller.login(form.username, form.password)
