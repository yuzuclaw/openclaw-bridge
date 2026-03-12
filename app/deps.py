from fastapi import Header, HTTPException
from app.config import settings


async def require_api_key(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {settings.bridge_api_key}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="unauthorized")
