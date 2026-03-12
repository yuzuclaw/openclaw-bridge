from pydantic import BaseModel, Field
from typing import Literal


class AgentHello(BaseModel):
    type: Literal['agent.hello'] = 'agent.hello'
    agent_id: str
    agent_name: str
    version: str
    hostname: str
    user_id: str | None = None
    device_id: str | None = None
    capabilities: list[str] = Field(default_factory=list)


class AgentHeartbeat(BaseModel):
    type: Literal['agent.heartbeat'] = 'agent.heartbeat'
    agent_id: str
    ts: str
    status: Literal['idle', 'busy', 'degraded'] = 'idle'
    running_tasks: int = 0


class TaskRun(BaseModel):
    type: Literal['task.run'] = 'task.run'
    task_id: str
    action: str
    input: dict = Field(default_factory=dict)
    timeout_sec: int = 30


class TaskResultMessage(BaseModel):
    type: Literal['task.result'] = 'task.result'
    task_id: str
    ok: bool
    result: dict
    finished_at: str
