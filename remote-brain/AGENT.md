# AGENT.md

## 远程大脑工作约定

1. 能脑内完成的事情，直接完成。
2. 需要本地真实信息时，调用中转平台。
3. 当前优先使用白名单动作：
   - `check_gateway_status`
   - `read_workspace_file`
   - `fetch_url`
   - `ollama_agent_run`
4. 若任务需要长期记忆，优先通过本地 OpenClaw 检索，而不是远程脑自己记流水账。
5. 若任务需要系统执行，最终执行权仍在本地 OpenClaw。
6. 未来 MCP 服务上线后，通过中转平台的 MCP façade 接入，而不是直接公网暴露本地 OpenClaw。
