import json
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from app.executors.local_command_exec import ALLOWED_COMMANDS
from app.executors.ollama_agent import LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL, LOCAL_LLM_PROVIDER, local_llm_config

ALLOWED_ACTIONS = {
    'fetch_url',
    'read_workspace_file',
    'local_command_exec',
    'check_gateway_status',
    'ollama_agent_run',
}

TASK_PLAN_JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        'action': {
            'type': 'string',
            'enum': sorted(ALLOWED_ACTIONS),
        },
        'input': {
            'type': 'object',
        },
    },
    'required': ['action', 'input'],
    'additionalProperties': False,
}

TASK_SYSTEM_PROMPT = f'''你是本地执行 agent 内部的“单步动作选择器”。
你的唯一职责：把一个自然语言任务压缩成且仅压缩成 1 个内部白名单动作 JSON，然后交给系统执行。

你只能输出 1 个 JSON 对象，且必须严格匹配这个结构：
{{
  "action": {json.dumps(sorted(ALLOWED_ACTIONS), ensure_ascii=False)},
  "input": {{ ... }}
}}

硬性规则：
1. 只能选择 1 个 action；不要生成多步计划、不要拆分子任务、不要建议后续编排。
2. 绝不能返回 task_execute，也绝不能返回任何未定义动作。
3. 不要输出解释、前后缀、markdown、代码块、注释；只输出 JSON 对象本身。
4. 如果任务是访问网页，优先用 fetch_url，input 只能包含：{{"url": "..."}}。
5. 如果任务是读取文件内容，优先用 read_workspace_file，input 只能包含：{{"path": "..."}}，或附带 offset/limit 整数。
6. 如果任务是执行简单本地命令，优先用 local_command_exec，且 command_id 只能是 {json.dumps(sorted(ALLOWED_COMMANDS), ensure_ascii=False)}。
7. 如果任务只是要求整理、摘要、解释、改写、生成文字，则用 ollama_agent_run，input 只能包含 task/context/timeout_sec。
8. 如果任务是查询 OpenClaw gateway 状态，则用 check_gateway_status，input 必须是空对象 {{}}。
9. 如果任务需要多个动作才能完成，也必须退化为最合适的单个动作，不得自行编排。
10. input 不能包含 schema 之外的额外字段。'''

URL_RE = re.compile(r'https?://[^\s)\]}>"\']+', re.IGNORECASE)
WORKSPACE_FILE_RE = re.compile(r'(/home/ubuntu/\.openclaw/workspace[^\s,;\]\)]+)', re.IGNORECASE)
OFFSET_RE = re.compile(r'offset\s*[=:：]?\s*(\d+)', re.IGNORECASE)
LIMIT_RE = re.compile(r'limit\s*[=:：]?\s*(\d+)', re.IGNORECASE)


def _extract_json_object(text: str) -> str | None:
    text = (text or '').strip()
    if not text:
        return None

    fence_start = text.find('```')
    if fence_start != -1:
        fenced = text[fence_start + 3:]
        if fenced.startswith('json'):
            fenced = fenced[4:]
        fence_end = fenced.find('```')
        if fence_end != -1:
            candidate = fenced[:fence_end].strip()
            if candidate:
                text = candidate

    decoder = json.JSONDecoder()
    for idx, ch in enumerate(text):
        if ch != '{':
            continue
        try:
            obj, end = decoder.raw_decode(text[idx:])
            if isinstance(obj, dict):
                trailing = text[idx + end:].strip()
                if trailing and not trailing.startswith('```'):
                    continue
                return json.dumps(obj, ensure_ascii=False)
        except Exception:
            continue
    return None


def _normalize_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f'{field_name} must be an integer')
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError(f'{field_name} must be an integer')


def _validate_plan(plan: Any) -> dict:
    if not isinstance(plan, dict):
        raise ValueError('planner did not return an object')

    extra_top = set(plan.keys()) - {'action', 'input'}
    if extra_top:
        raise ValueError(f'planner returned unexpected top-level fields: {sorted(extra_top)}')

    action = plan.get('action')
    action_input = plan.get('input')

    if action not in ALLOWED_ACTIONS:
        raise ValueError(f'planner returned unsupported action: {action}')
    if not isinstance(action_input, dict):
        raise ValueError('planner input must be an object')

    if action == 'check_gateway_status':
        if action_input:
            raise ValueError('check_gateway_status input must be an empty object')
        return {'action': action, 'input': {}}

    if action == 'local_command_exec':
        extra = set(action_input.keys()) - {'command_id'}
        if extra:
            raise ValueError(f'local_command_exec input has unexpected fields: {sorted(extra)}')
        command_id = action_input.get('command_id')
        if command_id not in ALLOWED_COMMANDS:
            raise ValueError(f'command_id not allowed: {command_id}')
        return {'action': action, 'input': {'command_id': command_id}}

    if action == 'fetch_url':
        extra = set(action_input.keys()) - {'url'}
        if extra:
            raise ValueError(f'fetch_url input has unexpected fields: {sorted(extra)}')
        url = str(action_input.get('url', '') or '').strip()
        if not url:
            raise ValueError('fetch_url input.url is required')
        return {'action': action, 'input': {'url': url}}

    if action == 'read_workspace_file':
        extra = set(action_input.keys()) - {'path', 'offset', 'limit'}
        if extra:
            raise ValueError(f'read_workspace_file input has unexpected fields: {sorted(extra)}')
        path = str(action_input.get('path', '') or '').strip()
        if not path:
            raise ValueError('read_workspace_file input.path is required')
        normalized_input = {'path': path}
        if 'offset' in action_input:
            normalized_input['offset'] = _normalize_int(action_input['offset'], 'offset')
        if 'limit' in action_input:
            normalized_input['limit'] = _normalize_int(action_input['limit'], 'limit')
        return {'action': action, 'input': normalized_input}

    if action == 'ollama_agent_run':
        extra = set(action_input.keys()) - {'task', 'context', 'timeout_sec'}
        if extra:
            raise ValueError(f'ollama_agent_run input has unexpected fields: {sorted(extra)}')
        task = str(action_input.get('task', '') or '').strip()
        if not task:
            raise ValueError('ollama_agent_run input.task is required')
        normalized_input = {'task': task}
        context = action_input.get('context', {})
        if context is None:
            context = {}
        if not isinstance(context, dict):
            raise ValueError('ollama_agent_run input.context must be an object')
        normalized_input['context'] = context
        if 'timeout_sec' in action_input:
            normalized_input['timeout_sec'] = _normalize_int(action_input['timeout_sec'], 'timeout_sec')
        return {'action': action, 'input': normalized_input}

    raise ValueError(f'unhandled action validation branch: {action}')


def _extract_first_url(task: str) -> str | None:
    match = URL_RE.search(task or '')
    if not match:
        return None
    url = match.group(0).rstrip('.,!?')
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return url


def _extract_workspace_path(task: str) -> str | None:
    match = WORKSPACE_FILE_RE.search(task or '')
    if not match:
        return None
    return match.group(1).rstrip('.,!?')


def _extract_optional_window(task: str) -> dict:
    extra = {}
    offset_match = OFFSET_RE.search(task or '')
    limit_match = LIMIT_RE.search(task or '')
    if offset_match:
        extra['offset'] = int(offset_match.group(1))
    if limit_match:
        extra['limit'] = int(limit_match.group(1))
    return extra


def _heuristic_plan(task: str, context: dict, timeout_sec: int) -> dict:
    lowered = (task or '').strip().lower()
    task_cn = (task or '').strip()

    if any(key in lowered for key in ['gateway status', 'openclaw gateway', '检查网关状态']) or ('gateway' in lowered and 'status' in lowered):
        return {'action': 'check_gateway_status', 'input': {}}

    file_path = _extract_workspace_path(task_cn)
    if file_path:
        return {
            'action': 'read_workspace_file',
            'input': {
                'path': file_path,
                **_extract_optional_window(task_cn),
            },
        }

    if any(key in lowered for key in ['command_id: pwd', 'command_id=pwd']) or re.search(r'\bpwd\b', lowered):
        return {'action': 'local_command_exec', 'input': {'command_id': 'pwd'}}
    if any(key in lowered for key in ['ip addr', 'ip address', '网络地址', '网卡信息']):
        return {'action': 'local_command_exec', 'input': {'command_id': 'ip_addr'}}
    if 'gateway_status' in lowered:
        return {'action': 'local_command_exec', 'input': {'command_id': 'gateway_status'}}

    url = _extract_first_url(task_cn)
    if url:
        return {'action': 'fetch_url', 'input': {'url': url}}

    summary_hints = [
        '整理', '总结', '摘要', '改写', '解释', '翻译', '润色',
        'summarize', 'summary', 'rewrite', 'explain', 'translate',
    ]
    if any(hint in task_cn.lower() for hint in summary_hints) or context:
        return {
            'action': 'ollama_agent_run',
            'input': {
                'task': task_cn,
                'context': context,
                'timeout_sec': timeout_sec,
            },
        }

    return {
        'action': 'ollama_agent_run',
        'input': {
            'task': task_cn,
            'context': context,
            'timeout_sec': timeout_sec,
        },
    }


async def _plan_with_local_model(task: str, context: dict, timeout_sec: int) -> tuple[dict | None, dict | None]:
    if LOCAL_LLM_PROVIDER != 'ollama':
        return None, {
            'stage': 'planner_unavailable',
            'error': 'structured planner is only available for provider=ollama in the current implementation',
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
            'config': local_llm_config(),
        }

    if not LOCAL_LLM_BASE_URL or not LOCAL_LLM_MODEL:
        return None, {
            'stage': 'planner_unavailable',
            'error': 'local agent planner model is not configured',
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
            'config': local_llm_config(),
        }

    prompt = f"系统要求：{TASK_SYSTEM_PROMPT}\n\n任务：{task}\n上下文：{json.dumps(context, ensure_ascii=False)}\n\n只返回 1 个 JSON 对象。"
    payload = {
        'model': LOCAL_LLM_MODEL,
        'prompt': prompt,
        'stream': False,
        'format': TASK_PLAN_JSON_SCHEMA,
        'options': {
            'temperature': 0,
        },
    }
    timeout = httpx.Timeout(timeout_sec, connect=min(timeout_sec, 10.0))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{LOCAL_LLM_BASE_URL.rstrip('/')}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        return None, {
            'stage': 'planner_request',
            'error': 'task planner request to local agent model timed out',
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
            'base_url': LOCAL_LLM_BASE_URL,
            'timeout_sec': timeout_sec,
        }
    except httpx.HTTPError as exc:
        return None, {
            'stage': 'planner_request',
            'error': f'task planner request failed: {exc}',
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
            'base_url': LOCAL_LLM_BASE_URL,
        }

    content = (data.get('response', '') or '').strip()
    candidate = _extract_json_object(content)
    if not candidate:
        return None, {
            'stage': 'planner_parse',
            'error': 'task planner did not return a JSON object',
            'raw': content,
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
        }

    try:
        raw_plan = json.loads(candidate)
    except Exception:
        return None, {
            'stage': 'planner_parse',
            'error': 'task planner returned unparsable JSON',
            'raw': content,
            'candidate': candidate,
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
        }

    try:
        plan = _validate_plan(raw_plan)
    except Exception as exc:
        return None, {
            'stage': 'planner_validate',
            'error': str(exc),
            'raw': content,
            'candidate': candidate,
            'plan': raw_plan,
            'provider': LOCAL_LLM_PROVIDER,
            'model': LOCAL_LLM_MODEL,
        }

    return plan, {
        'stage': 'planner_ok',
        'provider': LOCAL_LLM_PROVIDER,
        'model': LOCAL_LLM_MODEL,
    }


async def task_execute(input_data: dict) -> dict:
    task = str(input_data.get('task', '') or '').strip()
    context = input_data.get('context', {})
    timeout_sec = int(input_data.get('timeout_sec', 180))

    if not task:
        return {
            'ok': False,
            'data': None,
            'error': 'task is required',
        }

    if not isinstance(context, dict):
        return {
            'ok': False,
            'data': None,
            'error': 'context must be an object',
        }

    heuristic_plan = _heuristic_plan(task, context, timeout_sec)
    heuristic_plan = _validate_plan(heuristic_plan)

    planner_meta: dict[str, Any] = {
        'strategy': 'heuristic',
        'model': LOCAL_LLM_MODEL,
        'provider': LOCAL_LLM_PROVIDER,
        'heuristic_plan': heuristic_plan,
    }

    plan = heuristic_plan

    should_try_planner = heuristic_plan['action'] == 'ollama_agent_run'
    if should_try_planner:
        planner_plan, planner_runtime = await _plan_with_local_model(task, context, timeout_sec)
        planner_meta['runtime'] = planner_runtime
        if planner_plan is not None:
            plan = planner_plan
            planner_meta['strategy'] = 'local-model'
        else:
            planner_meta['strategy'] = 'heuristic_fallback'

    from app.router.action_router import dispatch
    result = await dispatch(plan['action'], plan['input'])
    return {
        'ok': result.get('ok', False),
        'data': {
            'task': task,
            'plan': plan,
            'planner': planner_meta,
            'execution_result': result,
            'model': LOCAL_LLM_MODEL,
            'provider': LOCAL_LLM_PROVIDER,
            'config': local_llm_config(),
        },
        'error': None if result.get('ok', False) else result.get('error'),
    }
