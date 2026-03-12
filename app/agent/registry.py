from app.router.action_router import ACTION_MAP


def build_capabilities() -> list[str]:
    # Expose canonical names while keeping compatibility aliases internal.
    names = [name for name in ACTION_MAP.keys() if name != 'ollama_agent_run']
    return sorted(names)
