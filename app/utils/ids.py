from uuid import uuid4


def new_task_id() -> str:
    return f"task_{uuid4().hex[:12]}"
