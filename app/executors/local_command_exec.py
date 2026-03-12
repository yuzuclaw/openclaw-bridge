import asyncio

ALLOWED_COMMANDS = {
    "ip_addr": ["ip", "addr"],
    "gateway_status": ["openclaw", "gateway", "status"],
    "pwd": ["pwd"],
}


async def local_command_exec(input_data: dict) -> dict:
    command_id = input_data.get("command_id", "")
    argv = ALLOWED_COMMANDS.get(command_id)
    if not argv:
        return {
            "ok": False,
            "data": None,
            "error": f"command_id not allowed: {command_id}",
        }
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "ok": proc.returncode == 0,
        "data": {
            "command_id": command_id,
            "argv": argv,
            "stdout": (stdout or b"").decode(errors="ignore")[:20000],
            "stderr": (stderr or b"").decode(errors="ignore")[:8000],
            "returncode": proc.returncode,
        },
        "error": None if proc.returncode == 0 else f"command failed: {command_id}",
    }
