import httpx
from app.clients.base import BaseApiClient

class NotificationApiClient(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        super().__init__(client, service_name="notifications", base_url=base_url)

    async def send_email(self, payload: dict) -> dict:
        response = await self.request("POST", "emails", json=payload)
        return response.json()
