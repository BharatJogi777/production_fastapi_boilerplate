from typing import Any, cast

import httpx

from app.clients.base import BaseApiClient


class NotificationApiClient(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        super().__init__(client, service_name="notifications", base_url=base_url)

    async def send_email(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.request("POST", "emails", json=payload)
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("Notification API response must be a JSON object")
        return cast(dict[str, Any], result)
