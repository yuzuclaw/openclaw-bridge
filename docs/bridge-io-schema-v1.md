# Bridge 输入/输出 Schema v1（当前版本）

> 注意：本项目已收敛为“透明桥接 + 两把钥匙”：
> - Bearer：`BRIDGE_API_KEY`
> - Exec 签名：`EXEC_SIGNING_KEY`
> 并且本地执行由 Ubuntu 本机 OpenClaw 的真实 agent 承担（`transport=openclaw-cli`）。

## Base URL

- `{{BRIDGE_BASE_URL}}`（`http://127.0.0.1:8888`）

## 鉴权

> 模式 B（纯远程大脑）：远程大脑必须在会话启动时被注入以下两项密钥（秘密方式提供），才能发起请求并计算签名。
> - `BRIDGE_API_KEY`：平台提供的连接 token
> - `EXEC_SIGNING_KEY`：用户自己设定的执行密码
> 文档里只写占位符，不写明文值。

### 1) Bearer token（所有 /v1/* 必须）

```
Authorization: Bearer {{BRIDGE_API_KEY}}
```

### 2) 执行签名（执行类接口必须）

对以下接口必须带 `X-Exec-*`：
- `POST /v1/task/execute`
- `POST /v1/mcp/invoke`

签名规则：

```
msg = "{ts}.{nonce}.{method}.{path}.{raw_body}"
sig = HMAC_SHA256_HEX({{EXEC_SIGNING_KEY}}, msg)
```

Headers:

```
X-Exec-Timestamp: <unix_seconds>
X-Exec-Nonce: <random_hex>
X-Exec-Signature: <hex_hmac_sha256>
```

## 常见错误与处理

- `401 unauthorized`：Bearer token 不对（检查 `BRIDGE_API_KEY`）
- `401 missing exec signature`：缺少 `X-Exec-*` 三个 header（检查是否启用签名）
- `401 invalid exec signature`：执行密码不对（检查 `EXEC_SIGNING_KEY`）
- `401 exec signature expired`：时间戳过期（检查时钟/重试）
- `401 replayed nonce`：nonce 重放（生成新的 nonce 再试）

远程大脑应当在 401 时停止重试并向用户索取/确认 `BRIDGE_API_KEY` 与 `EXEC_SIGNING_KEY`（以秘密方式注入）。

## 接口

### GET /v1/healthz

无需 exec 签名，仅 Bearer。

### GET /v1/agents

列出 Ubuntu 本机 OpenClaw 里的真实 agents（用于选择 agent_id）。

### POST /v1/task/execute

用途：自然语言任务透明转发。

Request:

```json
{
  "agent_id": "local-exec-agent",
  "task": "ping baidu.com",
  "context": {},
  "timeout_sec": 60
}
```

Response（裁平）：

```json
{
  "ok": true,
  "agent_id": "local-exec-agent",
  "task": "ping baidu.com",
  "forwarded": true,
  "transport": "openclaw-cli",
  "text": "...",
  "raw": null,
  "error": null,
  "meta": {
    "durationMs": 1234,
    "aborted": false,
    "provider": "...",
    "model": "...",
    "sessionId": "..."
  }
}
```

### POST /v1/mcp/invoke

用途：结构化 payload 透明转发（最小 MCP façade）。

Request:

```json
{
  "agent_id": "local-exec-agent",
  "action": "<action_name>",
  "input": {},
  "timeout_sec": 30
}
```

Response：同样裁平（text/meta/raw/error）。
