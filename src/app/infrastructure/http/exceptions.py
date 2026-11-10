class ExternalServiceError(Exception):
    """An upstream service failed or returned an unsuccessful response."""
    def __init__(self, service: str, message: str, status_code: int | None = None) -> None:
        self.service = service
        self.message = message
        self.status_code = status_code
        super().__init__(f"{service}: {message}")
