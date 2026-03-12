import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.deps import require_api_key
from app.exec_auth import require_exec_signature
from app.openclaw_cli import run_local_openclaw_agent, trim_openclaw_meta

router = APIRouter(dependencies=[Depends(require_api_key), Depends(require_exec_signature)])


class McpInvokeRequest(BaseModel):
    agent_id: str
    action: str
    input: dict = Field(default_factory=dict)
    timeout_sec: int = 30


@router.get("/mcp/health")
async def mcp_health() -> dict:
    return {
        "ok": True,
        "service": "openclaw-bridge-mcp-relay",
        "version": "0.1.0",
        "note": "Transparent relay only: auth, routing, timeout, audit, result return.",
    }


@router.post("/mcp/invoke")
async def mcp_invoke(payload: McpInvokeRequest) -> dict:
    # Minimal transparent MCP relay: pass structured payload as a message to the real OpenClaw agent.
    message = json.dumps({"action": payload.action, "input": payload.input}, ensure_ascii=False)
    routed = await run_local_openclaw_agent(payload.agent_id, message, timeout_sec=payload.timeout_sec)
    return {
        'ok': routed.get('ok', False),
        'agent_id': payload.agent_id,
        'action': payload.action,
        'forwarded': True,
        'transport': 'openclaw-cli',
        'text': routed.get('text'),
        'raw': None,
        'error': routed.get('error'),
        'meta': trim_openclaw_meta(routed.get('data') or {}),
    }
