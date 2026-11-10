from typing import Annotated
import httpx
from fastapi import Depends, Request

def get_http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise RuntimeError("HTTP client is unavailable outside the application lifespan")
    return client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]
