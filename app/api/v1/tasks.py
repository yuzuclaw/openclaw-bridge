from fastapi import APIRouter, Depends, HTTPException
from app.deps import require_api_key
from app.schemas.tasks import TaskCreateRequest, TaskCreateResponse, TaskResponse
from app.repositories.task_repo import insert_task, get_task, update_task
from app.api.v1.agent_ws import dispatch_task_to_agent
from app.utils.ids import new_task_id
from app.utils.time import utc_now_iso

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/tasks", response_model=TaskCreateResponse)
async def create_task(payload: TaskCreateRequest) -> TaskCreateResponse:
    task_id = new_task_id()
    now = utc_now_iso()
    task = {
        "task_id": task_id,
        "client_task_id": payload.client_task_id,
        "agent_id": payload.agent_id,
        "action": payload.action,
        "status": "running",
        "input": payload.input,
        "result": None,
        "created_at": now,
        "updated_at": now,
    }
    insert_task(task)
    result = await dispatch_task_to_agent(
        payload.agent_id,
        {
            "type": "task.run",
            "task_id": task_id,
            "action": payload.action,
            "input": payload.input,
            "timeout_sec": payload.timeout_sec,
        },
        timeout_sec=payload.timeout_sec,
    )
    status = "succeeded" if result.get("ok") else "failed"
    update_task(task_id, status, result, utc_now_iso())
    return TaskCreateResponse(
        task_id=task_id,
        status=status,
        action=payload.action,
        agent_id=payload.agent_id,
        accepted=True,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_detail(task_id: str) -> TaskResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return TaskResponse(**task)
