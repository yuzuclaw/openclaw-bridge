# MEMORY.md

这里存放远程大脑可长期依赖的稳定记忆：

- 本地执行层：OpenClaw
- 本地低成本模型层：Ollama（当前计划使用飞牛 NAS 上的 `qwen3.5:2b`）
- 中转域名：`127.0.0.1`
- 中转平台职责：连接远程大脑、本地 OpenClaw、未来 MCP 客户端
- 本地长期记忆检索：依赖 OpenClaw + memory-lancedb-pro

注意：
- 凭证不写这里
- token / key 统一放 `secrets/INFRA.md`
