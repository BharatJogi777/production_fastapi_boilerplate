import httpx
import pytest
from app.clients.base import BaseApiClient
from app.infrastructure.http.exceptions import ExternalServiceError

@pytest.mark.asyncio
async def test_api_client_maps_upstream_errors():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        client = BaseApiClient(http, service_name="billing", base_url="https://billing.example")
        with pytest.raises(ExternalServiceError) as error:
            await client.request("GET", "/invoices")
        assert error.value.status_code == 503
