import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bridge_api_key: str = os.getenv("BRIDGE_API_KEY", "change-me")
    bridge_host: str = os.getenv("BRIDGE_HOST", "0.0.0.0")
    bridge_port: int = int(os.getenv("BRIDGE_PORT", "8888"))

    # Console Basic Auth (server-side)
    # For now: single-user console login.
    # If CONSOLE_BASIC_PASS is not set, it falls back to BRIDGE_API_KEY.
    console_basic_user: str = os.getenv("CONSOLE_BASIC_USER", "admin")
    console_basic_pass: str = os.getenv("CONSOLE_BASIC_PASS", "admin123...")

    # Additional request-signing key (HMAC) for execution endpoints.
    # Provide via environment. If empty, exec signature check is disabled.
    exec_signing_key: str = os.getenv("EXEC_SIGNING_KEY", "")


settings = Settings()
