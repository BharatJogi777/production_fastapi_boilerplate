from app.modules.auth.schemas import TokenResponse
from app.modules.auth.service import AuthService

class AuthController:
    def __init__(self, service: AuthService) -> None:
        self.service = service
    async def login(self, email: str, password: str) -> TokenResponse:
        return TokenResponse(access_token=await self.service.authenticate(email, password))
