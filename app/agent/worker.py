import asyncio
from app.router.action_router import dispatch
from app.utils.time import utc_now_iso


class TaskWorker:
    def __init__(self, send_json, max_concurrent: int = 2):
        self.send_json = send_json
        self.sem = asyncio.Semaphore(max_concurrent)
        self.running_tasks: set[str] = set()

    async def handle_task(self, msg: dict):
        asyncio.create_task(
            self._run_one(
                task_id=msg['task_id'],
                action=msg['action'],
                input_data=msg.get('input', {}),
                timeout_sec=int(msg.get('timeout_sec', 30)),
            )
        )

    async def _run_one(self, task_id: str, action: str, input_data: dict, timeout_sec: int):
        async with self.sem:
            self.running_tasks.add(task_id)
            try:
                result = await asyncio.wait_for(dispatch(action, input_data), timeout=timeout_sec)
                ok = bool(result.get('ok'))
            except asyncio.TimeoutError:
                ok = False
                result = {'ok': False, 'data': None, 'error': f'timeout after {timeout_sec}s'}
            except Exception as e:
                ok = False
                result = {'ok': False, 'data': None, 'error': str(e)}
            finally:
                self.running_tasks.discard(task_id)

            await self.send_json({
                'type': 'task.result',
                'task_id': task_id,
                'ok': ok,
                'result': result,
                'finished_at': utc_now_iso(),
            })
