import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings
from app.agent.state import AGENTS, ConnectedAgent, PENDING_RESULTS

router = APIRouter()


def _ws_unauthorized(token: str | None) -> bool:
    expected = f"Bearer {settings.bridge_api_key}"
    return token != expected


@router.websocket('/agent/ws')
async def agent_ws(websocket: WebSocket):
    auth = websocket.headers.get('authorization')
    if _ws_unauthorized(auth):
        await websocket.close(code=4401)
        return

    await websocket.accept()
    agent_id = None
    try:
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get('type')

            if msg_type == 'agent.hello':
                agent_id = msg['agent_id']
                AGENTS[agent_id] = ConnectedAgent(
                    agent_id=agent_id,
                    user_id=msg.get('user_id'),
                    device_id=msg.get('device_id'),
                    capabilities=msg.get('capabilities', []),
                    websocket=websocket,
                )
                await websocket.send_json({
                    'type': 'agent.hello.ack',
                    'ok': True,
                    'agent_id': agent_id,
                    'heartbeat_interval_sec': 20,
                })

            elif msg_type == 'agent.heartbeat' and agent_id in AGENTS:
                AGENTS[agent_id].running_tasks = int(msg.get('running_tasks', 0))
                await websocket.send_json({'type': 'server.pong'})

            elif msg_type == 'task.result':
                task_id = msg.get('task_id')
                fut = PENDING_RESULTS.get(task_id)
                if fut and not fut.done():
                    fut.set_result(msg)

            else:
                await websocket.send_json({
                    'type': 'error',
                    'error': f'unsupported message type: {msg_type}'
                })
    except WebSocketDisconnect:
        pass
    finally:
        if agent_id and agent_id in AGENTS:
            AGENTS.pop(agent_id, None)


async def dispatch_task_to_agent(agent_id: str, task: dict, timeout_sec: int = 30) -> dict:
    agent = AGENTS.get(agent_id)
    if not agent:
        return {'ok': False, 'error': 'agent_offline', 'data': None}

    fut = asyncio.get_event_loop().create_future()
    task_id = task['task_id']
    PENDING_RESULTS[task_id] = fut
    await agent.websocket.send_json(task)

    try:
        result = await asyncio.wait_for(fut, timeout=timeout_sec)
        return {'ok': True, 'data': result, 'error': None}
    except asyncio.TimeoutError:
        return {'ok': False, 'error': f'task timeout after {timeout_sec}s', 'data': None}
    finally:
        PENDING_RESULTS.pop(task_id, None)
