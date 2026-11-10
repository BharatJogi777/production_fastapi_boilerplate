from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db_session
from app.modules.auth.controller import AuthController
from app.modules.auth.schemas import RegisterRequest, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead
from app.modules.users.service import UserService

router = APIRouter()

def get_auth_controller(session: AsyncSession = Depends(get_db_session)) -> AuthController:
    return AuthController(AuthService(UserRepository(session), session))

@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db_session)) -> UserRead:
    user = await UserService(UserRepository(session), session).register(
        str(payload.email), payload.password)
    return UserRead.model_validate(user)

@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller)) -> TokenResponse:
    return await controller.login(form.username, form.password)
