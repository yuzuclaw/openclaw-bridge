from fastapi import APIRouter
from app.schemas.health import HealthzResponse
from app.utils.time import utc_now_iso

router = APIRouter()


@router.get("/healthz", response_model=HealthzResponse)
async def healthz() -> HealthzResponse:
    return HealthzResponse(
        status="ok",
        service="openclaw-bridge",
        version="0.1.0",
        time=utc_now_iso(),
    )
