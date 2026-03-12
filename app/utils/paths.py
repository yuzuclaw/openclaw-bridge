from pathlib import Path

WORKSPACE_ROOT = Path("/home/ubuntu/.openclaw/workspace").resolve()


def resolve_workspace_path(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if WORKSPACE_ROOT not in path.parents and path != WORKSPACE_ROOT:
        raise ValueError("path is outside workspace root")
    return path
