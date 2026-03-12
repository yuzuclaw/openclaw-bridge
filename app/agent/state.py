from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectedAgent:
    agent_id: str
    user_id: str | None
    device_id: str | None
    capabilities: list[str]
    websocket: Any
    running_tasks: int = 0


AGENTS: dict[str, ConnectedAgent] = {}
PENDING_RESULTS: dict[str, Any] = {}
