import asyncio
import os
import socket

from app.agent.client import AgentWsClient
from app.agent.worker import TaskWorker
from app.agent.heartbeat import heartbeat_loop
from app.agent.registry import build_capabilities

AGENT_ID = os.getenv('AGENT_ID', 'local-exec-agent')
AGENT_NAME = os.getenv('AGENT_NAME', 'local-openclaw-bridge')
VERSION = os.getenv('AGENT_VERSION', '0.1.0')
RELAY_WS_URL = os.getenv('RELAY_WS_URL', 'ws://127.0.0.1:8888/v1/agent/ws')
RELAY_API_KEY = os.getenv('RELAY_API_KEY', 'change-me')
HEARTBEAT_INTERVAL_SEC = int(os.getenv('HEARTBEAT_INTERVAL_SEC', '20'))
AGENT_USER_ID = os.getenv('AGENT_USER_ID', 'mark')
AGENT_DEVICE_ID = os.getenv('AGENT_DEVICE_ID', socket.gethostname())


async def run_forever():
    backoff = 3
    while True:
        client = AgentWsClient(
            url=RELAY_WS_URL,
            headers={'Authorization': f'Bearer {RELAY_API_KEY}'},
        )
        hb_task = None
        try:
            await client.connect()
            worker = TaskWorker(send_json=client.send_json, max_concurrent=2)

            await client.send_json({
                'type': 'agent.hello',
                'agent_id': AGENT_ID,
                'agent_name': AGENT_NAME,
                'version': VERSION,
                'hostname': socket.gethostname(),
                'user_id': AGENT_USER_ID,
                'device_id': AGENT_DEVICE_ID,
                'capabilities': build_capabilities(),
            })

            hb_task = asyncio.create_task(
                heartbeat_loop(client.send_json, AGENT_ID, worker, interval_sec=HEARTBEAT_INTERVAL_SEC)
            )
            backoff = 3

            while True:
                msg = await client.recv_json()
                if msg.get('type') == 'task.run':
                    await worker.handle_task(msg)
                elif msg.get('type') == 'server.ping':
                    await client.send_json({'type': 'server.pong'})
                else:
                    print(f'[agent] ignore message: {msg}')
        except Exception as e:
            print(f'[agent] disconnected: {e}; retry in {backoff}s')
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
        finally:
            if hb_task:
                hb_task.cancel()
            try:
                await client.close()
            except Exception:
                pass


if __name__ == '__main__':
    asyncio.run(run_forever())
