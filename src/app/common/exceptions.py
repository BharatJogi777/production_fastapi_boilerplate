class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message, self.status_code = message, status_code
        super().__init__(message)
class ConflictError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 409)
class AuthenticationError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password", 401)
class ForbiddenError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Account is inactive", 403)
