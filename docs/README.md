# openclaw-bridge docs

当前 docs 已收敛到“透明桥接 + 两把钥匙（Bearer + Exec 签名）+ 本机 OpenClaw agent 执行（transport=openclaw-cli）”。

密钥策略（模式 B：纯远程大脑）：
- 平台提供连接 token：`BRIDGE_API_KEY`
- 用户自定执行密码：`EXEC_SIGNING_KEY`
- 文档与 prompt 只写占位符，不写明文值；密钥在会话启动时以秘密方式注入。

保留文档：
- `remote-brain-generic-prompt.md`：远程大脑通用提示模板（包含请求/验证/回包判定）
- `bridge-io-schema-v1.md`：当前 bridge 输入/输出协议（含签名规则）
- `remote-brain-sample-eval-template.md`：样本记录与评估模板

说明：
- 旧的 ChatGPT/Gemini 专用 prompt、旧 tasks 模式、旧 websocket local-daemon 协议、旧“本地白名单 action”框架文档已删除（避免误导）。
