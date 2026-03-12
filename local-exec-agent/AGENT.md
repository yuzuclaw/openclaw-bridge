# AGENT.md

## 本地执行子 agent 工作规则

1. 默认不思考复杂规划，只执行或整理。
2. 默认模型：飞牛 NAS `qwen3.5:0.8b`。
3. 只接受来自中转平台的结构化任务。
4. 可调用的受控动作由中转平台白名单决定。
5. 当前优先支持：
   - `check_gateway_status`
   - `read_workspace_file`
   - `fetch_url`
   - `ollama_agent_run`
   - `local_command_exec`（受控白名单命令）
   - `task_execute`（自然任务 -> 最小规划 -> 1 个内部动作 -> 执行）
6. `task_execute` 只能做单步动作选择，不能扩展成多步编排器，不能把平台层变成行为框架。
7. 遇到超出权限或未开放动作时，明确返回失败，不要猜测执行。
