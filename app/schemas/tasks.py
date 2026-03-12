from typing import Literal
from pydantic import BaseModel, Field

TaskStatus = Literal["pending", "running", "succeeded", "failed"]


class TaskCreateRequest(BaseModel):
    agent_id: str
    action: str
    input: dict = Field(default_factory=dict)
    client_task_id: str | None = None
    timeout_sec: int = 30


class TaskCreateResponse(BaseModel):
    task_id: str
    status: TaskStatus
    action: str
    agent_id: str
    accepted: bool = True


class TaskResult(BaseModel):
    ok: bool
    data: dict | None = None
    error: str | None = None


class TaskResponse(BaseModel):
    task_id: str
    client_task_id: str | None = None
    agent_id: str | None = None
    action: str
    status: TaskStatus
    input: dict
    result: TaskResult | None = None
    created_at: str
    updated_at: str
