from fastapi import APIRouter, Depends
from app.deps import require_api_key
from app.openclaw_cli import list_local_openclaw_agents

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get('/agents')
async def list_agents() -> dict:
    result = await list_local_openclaw_agents()
    return {
        'ok': result.get('ok', False),
        'count': len(result.get('agents', [])),
        'agents': result.get('agents', []),
        'error': result.get('error'),
    }
