import asyncio
import json
import re
from pathlib import Path
from typing import Any

OPENCLAW_BIN = "openclaw"
AGENTS_DIR = Path.home() / ".openclaw" / "agents"
AGENT_LINE_RE = re.compile(r"^-\s+([a-zA-Z0-9._-]+)(?:\s+\((.*?)\))?$")


async def _run_command(args: list[str], timeout_sec: int = 120) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
        return proc.returncode, stdout_b.decode("utf-8", errors="replace"), stderr_b.decode("utf-8", errors="replace")
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 124, "", f"command timeout after {timeout_sec}s: {' '.join(args)}"


async def list_local_openclaw_agents() -> dict[str, Any]:
    code, stdout, stderr = await _run_command([OPENCLAW_BIN, "agents", "list"], timeout_sec=60)
    if code != 0:
        return {
            "ok": False,
            "agents": [],
            "error": stderr.strip() or stdout.strip() or f"openclaw agents list exited with {code}",
        }

    agents: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in stdout.splitlines():
        line = raw_line.rstrip()
        m = AGENT_LINE_RE.match(line)
        if m:
            current = {
                "agent_id": m.group(1),
                "display_name": m.group(2),
                "workspace": None,
                "agent_dir": None,
                "model": None,
                "routing_rules": None,
                "source": "openclaw",
                "available": True,
            }
            agents.append(current)
            continue
        if not current:
            continue
        stripped = line.strip()
        if stripped.startswith("Workspace:"):
            current["workspace"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Agent dir:"):
            current["agent_dir"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Model:"):
            current["model"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Routing rules:"):
            current["routing_rules"] = stripped.split(":", 1)[1].strip()

    # Fallback from filesystem if parsing produced nothing.
    if not agents and AGENTS_DIR.exists():
        for d in sorted(AGENTS_DIR.iterdir()):
            if d.is_dir():
                agents.append({
                    "agent_id": d.name,
                    "display_name": None,
                    "workspace": None,
                    "agent_dir": str(d),
                    "model": None,
                    "routing_rules": None,
                    "source": "filesystem",
                    "available": True,
                })

    return {"ok": True, "agents": agents, "error": None, "raw": stdout}


def _extract_text_from_openclaw_run(payload: dict[str, Any]) -> str | None:
    """Pick the most useful human-facing text from an OpenClaw run JSON."""
    try:
        payloads = payload.get('result', {}).get('payloads', [])
        if not isinstance(payloads, list) or not payloads:
            return None

        texts: list[str] = []
        for item in payloads:
            if isinstance(item, dict) and isinstance(item.get('text'), str):
                t = item.get('text').strip()
                if t:
                    texts.append(t)

        if not texts:
            return None

        # Prefer non-abort/timeout messages if present.
        bad_prefixes = (
            'request was aborted',
            'request timed out',
            'request timed out before',
        )
        for t in texts[::-1]:
            if t.lower().startswith(bad_prefixes):
                continue
            return t

        # Fallback to last text.
        return texts[-1]
    except Exception:
        return None


def trim_openclaw_meta(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Trim OpenClaw run meta to the small set needed for UI/debug.

    Removes large fields like systemPromptReport.
    """
    try:
        meta = payload.get('result', {}).get('meta')
        if not isinstance(meta, dict):
            return None
        agent_meta = meta.get('agentMeta') if isinstance(meta.get('agentMeta'), dict) else {}
        return {
            'durationMs': meta.get('durationMs'),
            'aborted': meta.get('aborted'),
            'provider': agent_meta.get('provider'),
            'model': agent_meta.get('model'),
            'sessionId': agent_meta.get('sessionId'),
        }
    except Exception:
        return None


async def run_local_openclaw_agent(agent_id: str, message: str, timeout_sec: int = 180) -> dict[str, Any]:
    args = [
        OPENCLAW_BIN,
        "agent",
        "--agent",
        agent_id,
        "--message",
        message,
        "--json",
        "--timeout",
        str(timeout_sec),
    ]
    code, stdout, stderr = await _run_command(args, timeout_sec=max(timeout_sec + 15, 30))
    if code != 0:
        return {
            "ok": False,
            "data": {
                "agent_id": agent_id,
                "message": message,
                "stderr": stderr,
                "stdout": stdout,
                "exit_code": code,
            },
            "error": stderr.strip() or stdout.strip() or f"openclaw agent exited with {code}",
        }

    try:
        payload = json.loads(stdout)
    except Exception:
        return {
            "ok": False,
            "data": {
                "agent_id": agent_id,
                "message": message,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": code,
            },
            "error": "openclaw agent did not return valid JSON",
        }

    return {
        "ok": True,
        "data": payload,
        "text": _extract_text_from_openclaw_run(payload),
        "error": None,
    }
