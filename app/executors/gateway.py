import asyncio


async def check_gateway_status(_: dict) -> dict:
    proc = await asyncio.create_subprocess_exec(
        "openclaw", "gateway", "status",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    raw = (stdout or b"").decode() + (stderr or b"").decode()
    return {
        "ok": proc.returncode == 0,
        "data": {
            "raw": raw.strip(),
            "returncode": proc.returncode,
        },
        "error": None if proc.returncode == 0 else "gateway status command failed",
    }
