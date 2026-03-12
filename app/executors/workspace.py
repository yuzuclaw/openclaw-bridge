from app.utils.paths import resolve_workspace_path


async def read_workspace_file(input_data: dict) -> dict:
    path = resolve_workspace_path(input_data["path"])
    offset = max(int(input_data.get("offset", 1)), 1)
    limit = max(int(input_data.get("limit", 200)), 1)
    lines = path.read_text(errors="ignore").splitlines()
    chunk = lines[offset - 1: offset - 1 + limit]
    return {
        "ok": True,
        "data": {
            "path": str(path),
            "offset": offset,
            "limit": limit,
            "content": "\n".join(chunk),
        },
        "error": None,
    }
