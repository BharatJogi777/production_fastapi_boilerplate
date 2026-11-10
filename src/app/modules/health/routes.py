from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db_session

router = APIRouter(tags=["health"])

@router.get("/health/live")
async def liveness() -> dict[str,str]:
    return {"status":"alive"}

@router.get("/health/ready")
async def readiness(session: AsyncSession = Depends(get_db_session)) -> dict[str,str]:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status":"ready"}
