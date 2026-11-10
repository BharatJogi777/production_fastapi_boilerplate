from typing import Any

import httpx

from app.infrastructure.http.exceptions import ExternalServiceError


class BaseApiClient:
    """Typed provider boundary around the shared HTTPX connection pool."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        service_name: str,
        base_url: str,
    ) -> None:
        self._client = client
        self._service_name = service_name
        self._base_url = base_url.rstrip("/") + "/"

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        url = self._base_url + path.lstrip("/")
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                self._service_name,
                "Upstream returned an unsuccessful status",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                self._service_name,
                "Upstream request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise ExternalServiceError(
                self._service_name,
                "Upstream request failed",
            ) from exc
