import secrets
from fastapi import Request, HTTPException
from fastapi.responses import Response

from app.config import settings

CONSOLE_USERNAME = settings.console_basic_user
CONSOLE_PASSWORD = settings.console_basic_pass or settings.bridge_api_key


def check_console_auth(request: Request) -> None:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": 'Basic realm="OpenClaw Bridge Console"'},
        )
    try:
        import base64
        encoded = auth[6:]
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": 'Basic realm="OpenClaw Bridge Console"'},
        )
    if not secrets.compare_digest(username, CONSOLE_USERNAME) or not secrets.compare_digest(
        password, CONSOLE_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": 'Basic realm="OpenClaw Bridge Console"'},
        )
