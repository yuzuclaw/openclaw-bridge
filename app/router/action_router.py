from app.executors.gateway import check_gateway_status
from app.executors.web import fetch_url
from app.executors.workspace import read_workspace_file
from app.executors.ollama_agent import ollama_agent_run as local_agent_llm_run
from app.executors.local_command_exec import local_command_exec
from app.executors.task_executor import task_execute


ACTION_MAP = {
    "check_gateway_status": check_gateway_status,
    "fetch_url": fetch_url,
    "read_workspace_file": read_workspace_file,
    "ollama_agent_run": local_agent_llm_run,
    "local_agent_llm_run": local_agent_llm_run,
    "local_command_exec": local_command_exec,
    "task_execute": task_execute,
}


async def dispatch(action: str, input_data: dict) -> dict:
    if action not in ACTION_MAP:
        return {"ok": False, "data": None, "error": f"unknown action: {action}"}
    return await ACTION_MAP[action](input_data)
