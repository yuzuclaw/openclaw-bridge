# MEMORY.md

长期稳定设定：

- 角色：本地执行子 agent
- 上游：`127.0.0.1`
- 本地执行网关：OpenClaw
- 本地廉价模型：飞牛 NAS 上的 `qwen3.5:0.8b`
- 目标：执行受控命令、整理结果、把结果回传远程大脑

注意：
- 真正的长期记忆检索依赖本地 OpenClaw / memory-lancedb-pro
- 凭证不写这里，统一在 `secrets/INFRA.md`
