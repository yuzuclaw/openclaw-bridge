import hmac
import hashlib
import secrets
import time
from typing import Dict

from fastapi import HTTPException, Request

from app.config import settings

# naive in-memory replay protection
_NONCE_SEEN: Dict[str, float] = {}
_NONCE_TTL_SEC = 600


def _prune() -> None:
    now = time.time()
    expired = [k for k, ts in _NONCE_SEEN.items() if now - ts > _NONCE_TTL_SEC]
    for k in expired:
        _NONCE_SEEN.pop(k, None)


def _hmac_hex(key: str, message: str) -> str:
    return hmac.new(key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()


async def require_exec_signature(request: Request) -> None:
    # If not configured, do not enforce. (You can enable by setting EXEC_SIGNING_KEY.)
    if not settings.exec_signing_key:
        return

    ts = request.headers.get("X-Exec-Timestamp")
    nonce = request.headers.get("X-Exec-Nonce")
    sig = request.headers.get("X-Exec-Signature")

    if not ts or not nonce or not sig:
        raise HTTPException(status_code=401, detail="missing exec signature")

    try:
        ts_int = int(ts)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid exec timestamp")

    now = int(time.time())
    if abs(now - ts_int) > 300:
        raise HTTPException(status_code=401, detail="exec signature expired")

    _prune()
    if nonce in _NONCE_SEEN:
        raise HTTPException(status_code=401, detail="replayed nonce")

    body = (await request.body()).decode("utf-8", errors="replace")
    msg = f"{ts_int}.{nonce}.{request.method}.{request.url.path}.{body}"
    expected = _hmac_hex(settings.exec_signing_key, msg)

    if not secrets.compare_digest(expected, sig):
        raise HTTPException(status_code=401, detail="invalid exec signature")

    _NONCE_SEEN[nonce] = time.time()
