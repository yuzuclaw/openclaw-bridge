import asyncio
from app.utils.time import utc_now_iso


async def heartbeat_loop(send_json, agent_id: str, worker, interval_sec: int = 20):
    while True:
        status = 'busy' if worker.running_tasks else 'idle'
        await send_json({
            'type': 'agent.heartbeat',
            'agent_id': agent_id,
            'ts': utc_now_iso(),
            'status': status,
            'running_tasks': len(worker.running_tasks),
        })
        await asyncio.sleep(interval_sec)
