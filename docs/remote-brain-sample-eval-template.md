# 远程大脑样本库与评估模板（适配透明转发版）

用于评估“远程大脑 → openclaw-bridge → Ubuntu 本机 OpenClaw agent”的效果。

## 每条样本建议记录字段

```json
{
  "sample_id": "sample-001",
  "user_request": "帮我 ping 一下 baidu.com",
  "bridge": {
    "base_url": "http://127.0.0.1",
    "agent_id": "local-exec-agent",
    "endpoint": "/v1/task/execute",
    "timeout_sec": 60
  },
  "auth": {
    "bearer": "used", 
    "exec_signature": "used",
    "note": "do not store BRIDGE_API_KEY/EXEC_SIGNING_KEY values in samples"
  },
  "bridge_response": {
    "ok": true,
    "transport": "openclaw-cli",
    "text": "...",
    "error": null,
    "meta": {
      "durationMs": 1234,
      "aborted": false,
      "provider": "...",
      "model": "..."
    }
  },
  "final_answer_ok": true,
  "notes": "..."
}
```

## 评估维度

- 理解是否正确
- 是否正确选择 endpoint（mcp vs task）
- 是否正确带 Bearer + exec signature
- 是否基于真实回包组织回答（不编造）
- 错误处理是否干净（401/timeout/retry）

## 常见失败标签

- `missing_bearer`
- `missing_exec_signature`
- `replayed_nonce`
- `expired_timestamp`
- `agent_timeout`
- `agent_aborted`
- `hallucinated_result`
- `over_call_bridge`
