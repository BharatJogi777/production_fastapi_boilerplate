import httpx
from app.core.config import get_settings

def build_http_client() -> httpx.AsyncClient:
    settings = get_settings()
    timeout = httpx.Timeout(
        connect=settings.http_connect_timeout_seconds,
        read=settings.http_read_timeout_seconds,
        write=settings.http_write_timeout_seconds,
        pool=settings.http_pool_timeout_seconds,
    )
    limits = httpx.Limits(
        max_connections=settings.http_max_connections,
        max_keepalive_connections=settings.http_max_keepalive_connections,
    )
    return httpx.AsyncClient(
        timeout=timeout, limits=limits, follow_redirects=False,
        headers={"User-Agent": f"{settings.app_name}/1.0"},
    )
