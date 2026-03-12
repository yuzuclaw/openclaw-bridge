from fastapi import APIRouter, Depends
from app.deps import require_api_key
from app.schemas.capabilities import CapabilitiesResponse

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def capabilities() -> CapabilitiesResponse:
    return CapabilitiesResponse(
        service="openclaw-bridge",
        version="0.1.0",
        mode="transparent-relay",
        relay_contract={
            "requires_agent_id": True,
            "supported_task_types": ["task.run"],
            "notes": [
                "Bridge only authenticates, routes, waits, audits, and returns results.",
                "Action semantics are owned by the remote brain and the local agent.",
                "Bridge does not define planner rules, tool schemas, or behavior frameworks.",
            ],
        },
    )
