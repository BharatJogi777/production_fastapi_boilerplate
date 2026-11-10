from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db_session
from app.modules.users.controller import UserController
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

def get_user_controller(session: AsyncSession = Depends(get_db_session)) -> UserController:
    return UserController(UserService(UserRepository(session), session))
