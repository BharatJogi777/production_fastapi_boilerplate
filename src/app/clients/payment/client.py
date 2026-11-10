from typing import Any, cast

import httpx

from app.clients.base import BaseApiClient


class PaymentApiClient(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        super().__init__(client, service_name="payments", base_url=base_url)

    async def get_payment(self, payment_id: str) -> dict[str, Any]:
        response = await self.request("GET", f"payments/{payment_id}")
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Payment API response must be a JSON object")
        return cast(dict[str, Any], payload)
