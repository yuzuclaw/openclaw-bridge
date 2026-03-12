import os
from typing import Any

import httpx

LOCAL_LLM_PROVIDER = os.getenv("LOCAL_AGENT_LLM_PROVIDER", "ollama").strip().lower()
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_AGENT_LLM_BASE_URL", "").strip()
LOCAL_LLM_MODEL = os.getenv("LOCAL_AGENT_LLM_MODEL", "").strip()
LOCAL_LLM_API_KEY = os.getenv("LOCAL_AGENT_LLM_API_KEY", "").strip()
LOCAL_LLM_CHAT_PATH = os.getenv("LOCAL_AGENT_LLM_CHAT_PATH", "/v1/chat/completions").strip() or "/v1/chat/completions"

SYSTEM_PROMPT = """你是本地 agent 自己配置的执行模型。
你的职责是：
1. 根据输入完成轻量执行辅助任务；
2. 优先输出简短、清楚、结构化的内容；
3. 不要假装拥有本地系统权限；
4. 如果任务需要真实系统状态、文件或网页内容，应由本地 agent 自己决定如何处理。"""


def local_llm_config() -> dict[str, Any]:
    return {
        "provider": LOCAL_LLM_PROVIDER,
        "base_url": LOCAL_LLM_BASE_URL,
        "model": LOCAL_LLM_MODEL,
        "chat_path": LOCAL_LLM_CHAT_PATH,
        "has_api_key": bool(LOCAL_LLM_API_KEY),
    }


def _config_error(message: str) -> dict:
    return {
        "ok": False,
        "data": {
            "local_llm": local_llm_config(),
        },
        "error": message,
    }


async def _generate_with_ollama(prompt: str, timeout_sec: int) -> dict:
    if not LOCAL_LLM_BASE_URL:
        return _config_error("local agent model is not configured: LOCAL_AGENT_LLM_BASE_URL is required for provider=ollama")
    if not LOCAL_LLM_MODEL:
        return _config_error("local agent model is not configured: LOCAL_AGENT_LLM_MODEL is required")

    payload = {
        "model": LOCAL_LLM_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    timeout = httpx.Timeout(timeout_sec, connect=min(timeout_sec, 10.0))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{LOCAL_LLM_BASE_URL.rstrip('/')}/api/generate", json=payload)
            data = resp.json()
    except httpx.TimeoutException:
        return {
            "ok": False,
            "data": {
                "local_llm": local_llm_config(),
                "timeout_sec": timeout_sec,
            },
            "error": "local agent llm request timed out",
        }
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "data": {
                "local_llm": local_llm_config(),
            },
            "error": f"local agent llm request failed: {exc}",
        }

    content = data.get("response", "")
    return {
        "ok": resp.status_code < 400,
        "data": {
            "provider": LOCAL_LLM_PROVIDER,
            "model": LOCAL_LLM_MODEL,
            "content": content,
            "base_url": LOCAL_LLM_BASE_URL,
        },
        "error": None if resp.status_code < 400 else f"llm status {resp.status_code}",
    }


async def _generate_with_openai_compatible(prompt: str, timeout_sec: int) -> dict:
    if not LOCAL_LLM_BASE_URL:
        return _config_error("local agent model is not configured: LOCAL_AGENT_LLM_BASE_URL is required for provider=openai/openrouter/custom")
    if not LOCAL_LLM_MODEL:
        return _config_error("local agent model is not configured: LOCAL_AGENT_LLM_MODEL is required")

    headers = {"Content-Type": "application/json"}
    if LOCAL_LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LOCAL_LLM_API_KEY}"

    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    url = f"{LOCAL_LLM_BASE_URL.rstrip('/')}/{LOCAL_LLM_CHAT_PATH.lstrip('/')}"
    timeout = httpx.Timeout(timeout_sec, connect=min(timeout_sec, 10.0))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()
    except httpx.TimeoutException:
        return {
            "ok": False,
            "data": {
                "local_llm": local_llm_config(),
                "timeout_sec": timeout_sec,
            },
            "error": "local agent llm request timed out",
        }
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "data": {
                "local_llm": local_llm_config(),
            },
            "error": f"local agent llm request failed: {exc}",
        }

    content = ""
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = ""

    return {
        "ok": resp.status_code < 400,
        "data": {
            "provider": LOCAL_LLM_PROVIDER,
            "model": LOCAL_LLM_MODEL,
            "content": content,
            "base_url": LOCAL_LLM_BASE_URL,
        },
        "error": None if resp.status_code < 400 else f"llm status {resp.status_code}",
    }


async def ollama_agent_run(input_data: dict) -> dict:
    task = input_data.get("task", "")
    context = input_data.get("context", {})
    timeout_sec = int(input_data.get("timeout_sec", 180))
    prompt = f"系统要求：{SYSTEM_PROMPT}\n\n任务：{task}\n上下文：{context}\n\n请直接给出结果。"

    if LOCAL_LLM_PROVIDER == "ollama":
        return await _generate_with_ollama(prompt, timeout_sec)

    if LOCAL_LLM_PROVIDER in {"openai", "openrouter", "custom"}:
        return await _generate_with_openai_compatible(prompt, timeout_sec)

    return _config_error(f"unsupported local agent model provider: {LOCAL_LLM_PROVIDER}")
