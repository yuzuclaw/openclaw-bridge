from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.deps import require_api_key
from app.exec_auth import require_exec_signature
from app.openclaw_cli import run_local_openclaw_agent, trim_openclaw_meta

router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_exec_signature)])


class TaskExecuteRequest(BaseModel):
    agent_id: str
    task: str
    context: dict = Field(default_factory=dict)
    timeout_sec: int = 180


@router.post('/task/execute')
async def task_execute_api(payload: TaskExecuteRequest) -> dict:
    # Transparent bridge behavior: pass the user's task text to the real local OpenClaw agent.
    # Context is preserved in the envelope for observability, but not reinterpreted by the bridge.
    message = payload.task if not payload.context else f"{payload.task}\n\n[bridge_context]\n{payload.context}"
    routed = await run_local_openclaw_agent(payload.agent_id, message, timeout_sec=payload.timeout_sec)
    return {
        'ok': routed.get('ok', False),
        'agent_id': payload.agent_id,
        'task': payload.task,
        'forwarded': True,
        'transport': 'openclaw-cli',
        'text': routed.get('text'),
        'raw': None,
        'error': routed.get('error'),
        'meta': trim_openclaw_meta(routed.get('data') or {}),
    }
