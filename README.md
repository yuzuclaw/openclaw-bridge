# openclaw-bridge

最小透明桥：打通远程大脑到本地 agent 的鉴权、路由、转发、超时、审计和结果回传链路。

默认本地联调地址使用 `ws://127.0.0.1:8888/v1/agent/ws`，真正部署到哪里由用户自己配，不在平台里写死。

## 架构原则

`127.0.0.1` / bridge 平台层 **不是行为框架**。
它只负责：
- 鉴权
- 路由
- 转发
- 审计/记录
- 超时
- 返回结果

它**不负责**：
- 定义动作语义
- 设计工具协议
- 规划自然语言任务
- 选择执行命令
- 编排多步流程
- 替本地 agent 补“规则框架”

也就是说：
- 远程大脑决定发什么
- 本地 agent 决定怎么理解、怎么执行、怎么配置自己的模型/provider
- bridge 只做中间透明桥接

## 运行

### 1) 启动 / 停止 bridge（推荐）

bridge 会从 `~/.openclaw/workspace/secrets/INFRA.md` 读取以下配置（以 `KEY=VALUE` 行形式写入）：
- `BRIDGE_API_KEY`（/v1 Bearer）
- `EXEC_SIGNING_KEY`（执行签名）
- `CONSOLE_BASIC_USER`（console BasicAuth 用户名）
- `CONSOLE_BASIC_PASS`（console BasicAuth 密码）

启动：

```bash
cd /home/ubuntu/.openclaw/workspace/projects/openclaw-bridge
bash scripts/start_bridge.sh
```

停止：

```bash
bash scripts/stop_bridge.sh
```

### 2) 启动本地 agent daemon

```bash
cd /home/ubuntu/.openclaw/workspace/projects/openclaw-bridge
source /tmp/openclaw-bridge-venv/bin/activate
export RELAY_API_KEY=change-me
# 下面这些都由“本地 agent 自己”决定，bridge 不做规定
export RELAY_WS_URL=ws://127.0.0.1:8888/v1/agent/ws
export LOCAL_AGENT_LLM_PROVIDER=ollama
export LOCAL_AGENT_LLM_BASE_URL=http://127.0.0.1:11434
export LOCAL_AGENT_LLM_MODEL=qwen3.5:0.8b
python -m app.agent.daemon
```

> 本地 agent 的模型/provider 由本地配置决定。可以是 Ollama、OpenRouter，或任意 OpenAI 兼容 / 自定义 API；bridge 不写死。

## 接口
- GET `/console`：浏览器调试页（token / relay contract / agents / mcp invoke / task execute / 四路链路面板）
- GET `/v1/healthz`
- GET `/v1/capabilities`（返回 bridge 的 relay contract，而不是动作框架）
- GET `/v1/agents`
- POST `/v1/mcp/invoke`
- POST `/v1/task/execute`
- POST `/v1/tasks`
- GET `/v1/tasks/{task_id}`
- WebSocket `/v1/agent/ws` (legacy/local experimentation path; current minimal path prefers the real OpenClaw agent via CLI for task relay)

Header:

```bash
Authorization: Bearer change-me
```

## 请求约定

### `/v1/mcp/invoke`
必须带 `agent_id`，bridge 会把 action + input 原样转给目标 agent。

示例：

```json
{
  "agent_id": "local-exec-agent",
  "action": "local_command_exec",
  "input": {"command_id": "pwd"},
  "timeout_sec": 30
}
```

### `/v1/task/execute`
必须带 `agent_id`，bridge 会把自然语言任务原样转给 Ubuntu 本机 OpenClaw 里的真实 agent。

当前最小实现路径是：
- bridge 调本机 `openclaw agent --agent <id> --message <task> --json`
- 由 OpenClaw 系统里的该 agent 自己决定模型/provider/能力
- bridge 只回传结果

> 注意：如果本地 agent 需要使用模型，那也是 OpenClaw 里该 agent 自己的配置；bridge 不规定 provider/model。

示例：

```json
{
  "agent_id": "local-exec-agent",
  "task": "把回收站的内容清空",
  "context": {},
  "timeout_sec": 180
}
```

### `/v1/tasks`
也是透明转发，只是带一个持久化 task 记录。

## Console 使用
访问：`http://127.0.0.1:8888/console`

Console 现在支持：
- Bearer token 输入并保存在浏览器本地
- 一键刷新 `healthz / capabilities / agents`
- 在线 agent 卡片展示，并可一键带入默认 `agent_id`
- 如果目标 agent 不在线，提交前前端就直接提示，不再傻等
- `POST /v1/mcp/invoke` 表单：透明转发 action + input
- `POST /v1/task/execute` 表单：透明转发自然语言任务
- “透明对话”组件：把远程文本原样发给本地 agent，并把本地返回整理成对话视图
- Console 不规定本地 agent 使用哪种模型/provider；仅负责把消息发到目标 agent 并展示返回
- 四路链路面板：远程发送 / 远程接收 / 本地发送 / 本地接收
- 发送请求后立即显示“本地端接收（推断 / pending）”，响应回来后再补“本地端发送”
- 访问根路径 `/` 时自动 307 跳转到 `/console`

调试约定：
- `agent_id` 必填
- bridge 不做本地直连执行
- bridge 不定义 action 白名单或 planner 规则
- 本地端两栏若出现“推断”，表示当前 API 没有单独暴露 agent 内部事件，只能依据请求/响应生命周期保守映射


## Public demo credentials (INSECURE)

This repository is published for collaboration and learning. The values below are **example/demo only**.

- Console (BasicAuth): `admin / admin123`
- API Bearer (`BRIDGE_API_KEY`): `api-key`
- Exec signing key (`EXEC_SIGNING_KEY`): `exec-key`

**Do not** use these values on a real public deployment.
