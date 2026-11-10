import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session

router = APIRouter(tags=["health"])
logger = structlog.get_logger()


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Process liveness only; deliberately does not depend on external systems."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    """Readiness checks mandatory dependencies before traffic is routed to this instance."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.warning("readiness_check_failed", dependency="database")
        raise HTTPException(status_code=503, detail="Required dependency unavailable") from None
    return {"status": "ready"}
