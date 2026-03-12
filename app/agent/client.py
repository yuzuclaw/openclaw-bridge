import json
import websockets


class AgentWsClient:
    def __init__(self, url: str, headers: dict):
        self.url = url
        self.headers = headers
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(
            self.url,
            additional_headers=self.headers,
            ping_interval=None,
            max_size=2 * 1024 * 1024,
        )

    async def send_json(self, payload: dict):
        await self.ws.send(json.dumps(payload, ensure_ascii=False))

    async def recv_json(self) -> dict:
        raw = await self.ws.recv()
        return json.loads(raw)

    async def close(self):
        if self.ws:
            await self.ws.close()
