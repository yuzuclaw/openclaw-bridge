from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from app.console_auth import check_console_auth

router = APIRouter(dependencies=[Depends(check_console_auth)])


HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenClaw Bridge Console</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1220;
      --panel: #121a2b;
      --panel-2: #18233a;
      --border: #2d3c5c;
      --text: #e8eefc;
      --muted: #9fb0d1;
      --accent: #6ea8fe;
      --accent-2: #8b5cf6;
      --ok: #22c55e;
      --warn: #f59e0b;
      --err: #ef4444;
      --remote: #60a5fa;
      --local: #a78bfa;
      --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      --sans: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      background: linear-gradient(180deg, #08101d 0%, #0b1220 100%);
      color: var(--text);
    }
    .wrap {
      max-width: 1680px;
      margin: 0 auto;
      padding: 24px;
    }
    h1, h2, h3 { margin: 0 0 10px; }
    p { margin: 0; color: var(--muted); }
    .hero {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    .hero .title { display: grid; gap: 10px; }
    .hero .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip {
      border: 1px solid var(--border);
      background: rgba(110,168,254,.08);
      color: var(--text);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
    }
    .layout {
      display: grid;
      grid-template-columns: 1.08fr .92fr;
      gap: 18px;
      align-items: start;
    }
    .panel {
      background: rgba(18, 26, 43, .92);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 8px 28px rgba(0,0,0,.22);
    }
    .panel + .panel { margin-top: 18px; }
    .section-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }
    .section-head .meta {
      font-size: 12px;
      color: var(--muted);
    }
    .grid-2, .grid-3 {
      display: grid;
      gap: 12px;
    }
    .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    label {
      display: grid;
      gap: 6px;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 10px;
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--border);
      background: #0e1729;
      color: var(--text);
      border-radius: 12px;
      padding: 10px 12px;
      font: inherit;
    }
    textarea {
      min-height: 120px;
      resize: vertical;
      font-family: var(--mono);
      line-height: 1.5;
    }
    .compact textarea { min-height: 90px; }
    .actions, .tiny-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    button {
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(110,168,254,.22), rgba(139,92,246,.16));
      color: var(--text);
      padding: 10px 14px;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
    }
    button.secondary { background: #13203a; }
    button.ghost { background: transparent; }
    button:disabled { opacity: .55; cursor: not-allowed; }
    .statusbar {
      display: grid;
      gap: 10px;
    }
    .status {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      padding: 10px 12px;
      border-radius: 12px;
      background: #0d1526;
      border: 1px solid var(--border);
      font-size: 13px;
    }
    .status strong { color: var(--text); }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      display: inline-block;
      margin-right: 8px;
      background: #64748b;
      box-shadow: 0 0 0 3px rgba(100,116,139,.15);
    }
    .ok { background: var(--ok); box-shadow: 0 0 0 3px rgba(34,197,94,.15); }
    .warn { background: var(--warn); box-shadow: 0 0 0 3px rgba(245,158,11,.15); }
    .err { background: var(--err); box-shadow: 0 0 0 3px rgba(239,68,68,.15); }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }
    .card {
      padding: 12px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: #0d1526;
    }
    .card h3 {
      font-size: 14px;
      margin-bottom: 8px;
    }
    .mini {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .hint {
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
      line-height: 1.5;
    }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: var(--mono);
      font-size: 12px;
      line-height: 1.55;
    }
    .log-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .log-panel {
      border: 1px solid var(--border);
      border-radius: 14px;
      background: #0d1526;
      overflow: hidden;
      min-height: 260px;
    }
    .log-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      background: #101a2e;
      flex-wrap: wrap;
    }
    .log-head h3 {
      font-size: 14px;
      margin: 0;
    }
    .log-head .meta {
      font-size: 11px;
      color: var(--muted);
    }
    .log-head.remote { border-left: 3px solid var(--remote); }
    .log-head.local { border-left: 3px solid var(--local); }
    .output {
      background: #08101d;
      min-height: 220px;
      max-height: 420px;
      overflow: auto;
      padding: 12px;
    }
    .entry {
      border: 1px solid #21304d;
      background: #0d1526;
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 12px;
    }
    .entry:last-child { margin-bottom: 0; }
    .entry-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
      flex-wrap: wrap;
      font-size: 12px;
      color: var(--muted);
    }
    .entry-head strong { color: var(--text); }
    .entry .req, .entry .res, .entry .note {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px dashed #2b3958;
    }
    .split {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }
    .kbd {
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--border);
      background: #0d1526;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      color: var(--muted);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      border: 1px solid var(--border);
      color: var(--muted);
      background: rgba(255,255,255,.03);
    }
    .badge.inferred {
      color: #fcd34d;
      border-color: rgba(252, 211, 77, .35);
      background: rgba(252, 211, 77, .08);
    }
    .badge.relay {
      color: #c4b5fd;
      border-color: rgba(196, 181, 253, .35);
      background: rgba(196, 181, 253, .08);
    }
    @media (max-width: 1300px) {
      .layout { grid-template-columns: 1fr; }
    }
    @media (max-width: 920px) {
      .log-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
      .wrap { padding: 16px; }
    }
  </style>
</head>
<body>
    <div class="wrap">
    <div class="hero">
      <div class="title">
        <div>
          <h1>OpenClaw Bridge Console</h1>
          <p>透明桥接调试台：鉴权、路由、agent 状态、任务转发、结果回传，不在平台侧定义行为框架。</p>
        </div>
        <div class="chips">
          <span class="chip">/v1/healthz</span>
          <span class="chip">/v1/capabilities</span>
          <span class="chip">/v1/agents</span>
          <span class="chip">/v1/mcp/invoke</span>
          <span class="chip">/v1/task/execute</span>
        </div>
      </div>
      <div class="chip">Console path: <strong>/console</strong></div>
    </div>

    <div class="layout">
      <div>
        <section class="panel">
          <div class="section-head">
            <div>
              <h2>连接与调试设置</h2>
              <div class="meta">API Bearer token（BRIDGE_API_KEY）。仅用于调用 /v1/* API；Console 登录使用浏览器 BasicAuth（独立账号密码）。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="copyCurlHealth()">复制 health curl</button>
              <button class="secondary" onclick="copyCurlAgents()">复制 agents curl</button>
            </div>
          </div>

          <div class="grid-3">
            <label>
              Bearer token
              <input id="token" placeholder="change-me" autocomplete="off" />
            </label>
            <label>
              执行签名 key（EXEC_SIGNING_KEY）
              <input id="execKey" placeholder="exec-signing-key" autocomplete="off" />
            </label>
            <label>
              默认 agent_id
              <input id="defaultAgentId" placeholder="local-exec-agent" value="local-exec-agent" />
            </label>
          </div>

          <div class="actions">
            <button onclick="refreshOverview()">刷新概览</button>
            <button class="secondary" onclick="loadCapabilities()">只刷新 capabilities</button>
            <button class="secondary" onclick="loadAgents()">只刷新 agents</button>
            <button class="ghost" onclick="clearAllLogs()">清空四路日志</button>
          </div>

          <div class="hint">
            bridge 只做透明转发。要测试任何任务，请先让本地 agent daemon 连上 bridge，随后 agents 区域里应能看到 <span class="kbd">local-exec-agent</span>。
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <div>
              <h2>服务概览</h2>
              <div class="meta">快速看 bridge 活着没、转发合同是否正常、agent 是否在线。</div>
            </div>
          </div>
          <div class="statusbar">
            <div class="status"><span><span id="healthDot" class="status-dot"></span><strong>Health</strong></span><span id="healthStatus">未检查</span></div>
            <div class="status"><span><span id="capDot" class="status-dot"></span><strong>Capabilities</strong></span><span id="capStatus">未加载</span></div>
            <div class="status"><span><span id="agentsDot" class="status-dot"></span><strong>Agents</strong></span><span id="agentsStatus">未加载</span></div>
          </div>

          <div style="height:12px"></div>
          <div id="agentCards" class="cards"></div>
          <div style="height:12px"></div>
          <div id="capabilityCards" class="cards"></div>
        </section>

        <section class="panel compact">
          <div class="section-head">
            <div>
              <h2>MCP Invoke</h2>
              <div class="meta">透明转发 action + input。bridge 不解释动作语义，只负责把它转给目标 agent。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="fillInvokePwd()">PWD 示例</button>
              <button class="secondary" onclick="fillInvokeGateway()">Gateway 示例</button>
              <button class="secondary" onclick="fillInvokeFetch()">Fetch URL 示例</button>
            </div>
          </div>

          <div class="grid-3">
            <label>
              agent_id（必填）
              <input id="invokeAgentId" placeholder="local-exec-agent" />
            </label>
            <label>
              action
              <select id="invokeAction"></select>
            </label>
            <label>
              timeout_sec
              <input id="invokeTimeout" type="number" value="30" min="1" step="1" />
            </label>
          </div>

          <label>
            input JSON
            <textarea id="invokeInput"></textarea>
          </label>

          <div class="actions">
            <button onclick="submitInvoke()">发送 /v1/mcp/invoke</button>
            <button class="secondary" onclick="copyInvokePayload()">复制 payload</button>
          </div>
        </section>

        <section class="panel compact">
          <div class="section-head">
            <div>
              <h2>Task Execute</h2>
              <div class="meta">透明转发自然语言任务。如何理解、规划、执行，完全由本地 agent 自己决定。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="fillTaskReadme()">读取 README 示例</button>
              <button class="secondary" onclick="fillTaskBaidu()">网页示例</button>
              <button class="secondary" onclick="fillTaskSummarize()">整理示例</button>
            </div>
          </div>

          <div class="grid-2">
            <label>
              agent_id（必填）
              <input id="taskAgentId" placeholder="local-exec-agent" />
            </label>
            <label>
              timeout_sec
              <input id="taskTimeout" type="number" value="180" min="1" step="1" />
            </label>
          </div>

          <label>
            自然语言任务
            <textarea id="taskText"></textarea>
          </label>

          <label>
            context JSON
            <textarea id="taskContext">{}</textarea>
          </label>

          <div class="actions">
            <button onclick="submitTaskExecute()">发送 /v1/task/execute</button>
            <button class="secondary" onclick="copyTaskPayload()">复制 payload</button>
          </div>
        </section>


        <section class="panel compact">
          <div class="section-head">
            <div>
              <h2>透明对话</h2>
              <div class="meta">把远程文本原样转给本地 agent 的 <span class="kbd">task_execute</span>，bridge 不解释、不改写。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="fillChatHello()">你好示例</button>
              <button class="secondary" onclick="fillChatTrash()">清空回收站示例</button>
              <button class="ghost" onclick="clearChatTranscript()">清空对话</button>
            </div>
          </div>

          <div class="grid-2">
            <label>
              agent_id（必填）
              <input id="chatAgentId" placeholder="local-exec-agent" />
            </label>
            <label>
              timeout_sec
              <input id="chatTimeout" type="number" value="180" min="1" step="1" />
            </label>
          </div>

          <label>
            远程要说的话
            <textarea id="chatInput" placeholder="比如：你好 / 清空回收站 / 帮我读取某个文件"></textarea>
          </label>

          <div class="actions">
            <button onclick="submitRelayChat()">发送到本地 agent</button>
            <button class="secondary" onclick="copyChatPayload()">复制 task payload</button>
          </div>

          <div class="hint">
            这是“对话式透明转发”壳子：本质仍然是调 <span class="kbd">/v1/task/execute</span>，只是把远程输入和本地返回整理成对话视图。
          </div>

          <div id="chatTranscript" class="output" style="margin-top:12px; max-height:360px"><div class="mini">还没有对话。</div></div>
        </section>

        <section class="panel compact">
          <div class="section-head">
            <div>
              <h2>最近请求模板</h2>
              <div class="meta">把常用 invoke / task 请求存成模板，后面一键回填，不用反复粘贴。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="saveCurrentAsTemplate()">保存当前表单为模板</button>
              <button class="ghost" onclick="clearTemplates()">清空模板</button>
            </div>
          </div>

          <div class="grid-2">
            <label>
              模板名称
              <input id="templateName" placeholder="比如：agent-pwd / task-readme / fetch-example" />
            </label>
            <label>
              模板类型
              <select id="templateType">
                <option value="mcp">MCP Invoke</option>
                <option value="task">Task Execute</option>
              </select>
            </label>
          </div>

          <div class="hint">
            自动保存最近 8 个模板到浏览器 localStorage。点“载入”会把内容回填到对应表单；点“覆写为当前”会用当前表单替换原模板。
          </div>

          <div id="templateList" class="cards" style="margin-top:12px"></div>
        </section>
      </div>

      <div>
        <section class="panel">
          <div class="section-head">
            <div>
              <h2>四路链路面板</h2>
              <div class="meta">拆分成远程/本地、发送/接收四个独立流。bridge 只展示转发生命周期；本地侧若无真实事件流，只做保守推断并显式标注“推断”。</div>
            </div>
            <div class="tiny-actions">
              <button class="secondary" onclick="scrollAllLogsTop()">全部到顶部</button>
              <button class="secondary" onclick="scrollAllLogsBottom()">全部到底部</button>
            </div>
          </div>

          <div class="log-grid">
            <div class="log-panel">
              <div class="log-head remote">
                <div>
                  <h3>远程端发送</h3>
                  <div class="meta">console -> bridge / relay 的出站请求</div>
                </div>
                <div id="remoteSentCount" class="meta">0 条</div>
              </div>
              <div id="remoteSent" class="output"><div class="mini">等待操作…</div></div>
            </div>

            <div class="log-panel">
              <div class="log-head remote">
                <div>
                  <h3>远程端接收</h3>
                  <div class="meta">bridge / relay -> console 的回包</div>
                </div>
                <div id="remoteRecvCount" class="meta">0 条</div>
              </div>
              <div id="remoteRecv" class="output"><div class="mini">等待操作…</div></div>
            </div>

            <div class="log-panel">
              <div class="log-head local">
                <div>
                  <h3>本地端发送</h3>
                  <div class="meta">agent / 本地执行侧 -> bridge 的返回、结果或状态回传</div>
                </div>
                <div id="localSentCount" class="meta">0 条</div>
              </div>
              <div id="localSent" class="output"><div class="mini">等待操作…</div></div>
            </div>

            <div class="log-panel">
              <div class="log-head local">
                <div>
                  <h3>本地端接收</h3>
                  <div class="meta">agent / 本地执行侧收到任务、动作或调度输入</div>
                </div>
                <div id="localRecvCount" class="meta">0 条</div>
              </div>
              <div id="localRecv" class="output"><div class="mini">等待操作…</div></div>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <div>
              <h2>使用提示</h2>
              <div class="meta">别过度设计，先把链路测通。</div>
            </div>
          </div>
          <div class="split mini">
1. 先点“刷新概览”，确认 health / capabilities / agents 正常。
2. agents 为空时，bridge 没有可转发目标，任何任务都不会执行。
3. MCP Invoke 只是把 action + input 原样转给本地 agent。
4. Task Execute 只是把自然语言任务原样转给本地 agent。
5. bridge 不负责解释动作、不负责规划任务、不负责定义执行框架。
6. 本地端两栏若出现“推断”，表示当前 API 没有单独暴露 agent 内部事件，只能依据请求/响应生命周期保守映射。
          </div>
        </section>
      </div>
    </div>
  </div>

<script>
const MAX_LOG_ENTRIES = 80;

const TEMPLATE_STORAGE_KEY = 'openclaw_bridge_recent_templates';
const MAX_TEMPLATES = 8;

const state = {
  agents: [],
  templates: [],
  logCounts: {
    remoteSent: 0,
    remoteRecv: 0,
    localSent: 0,
    localRecv: 0,
  },
};

const els = {
  token: document.getElementById('token'),
  execKey: document.getElementById('execKey'),
  defaultAgentId: document.getElementById('defaultAgentId'),
  invokeAgentId: document.getElementById('invokeAgentId'),
  invokeAction: document.getElementById('invokeAction'),
  invokeInput: document.getElementById('invokeInput'),
  invokeTimeout: document.getElementById('invokeTimeout'),
  taskAgentId: document.getElementById('taskAgentId'),
  taskText: document.getElementById('taskText'),
  taskContext: document.getElementById('taskContext'),
  taskTimeout: document.getElementById('taskTimeout'),
  chatAgentId: document.getElementById('chatAgentId'),
  chatInput: document.getElementById('chatInput'),
  chatTimeout: document.getElementById('chatTimeout'),
  chatTranscript: document.getElementById('chatTranscript'),
  templateName: document.getElementById('templateName'),
  templateType: document.getElementById('templateType'),
  templateList: document.getElementById('templateList'),
  remoteSent: document.getElementById('remoteSent'),
  remoteRecv: document.getElementById('remoteRecv'),
  localSent: document.getElementById('localSent'),
  localRecv: document.getElementById('localRecv'),
  remoteSentCount: document.getElementById('remoteSentCount'),
  remoteRecvCount: document.getElementById('remoteRecvCount'),
  localSentCount: document.getElementById('localSentCount'),
  localRecvCount: document.getElementById('localRecvCount'),
  healthDot: document.getElementById('healthDot'),
  capDot: document.getElementById('capDot'),
  agentsDot: document.getElementById('agentsDot'),
  healthStatus: document.getElementById('healthStatus'),
  capStatus: document.getElementById('capStatus'),
  agentsStatus: document.getElementById('agentsStatus'),
  capabilityCards: document.getElementById('capabilityCards'),
  agentCards: document.getElementById('agentCards'),
};

function init() {
  const savedToken = localStorage.getItem('openclaw_bridge_token') || 'change-me';
const savedExecKey = localStorage.getItem('openclaw_bridge_exec_key') || '';
  const savedAgent = localStorage.getItem('openclaw_bridge_default_agent') || 'local-exec-agent';
  els.token.value = savedToken;
els.execKey.value = savedExecKey;
  els.defaultAgentId.value = savedAgent;
  els.invokeAgentId.value = savedAgent;
  els.taskAgentId.value = savedAgent;
  els.chatAgentId.value = savedAgent;
  fillInvokePwd();
  fillTaskReadme();
  loadTemplates();
  refreshOverview();
}

function persistInputs() {
  localStorage.setItem('openclaw_bridge_token', els.token.value.trim());
  localStorage.setItem('openclaw_bridge_exec_key', els.execKey.value.trim());
  localStorage.setItem('openclaw_bridge_default_agent', els.defaultAgentId.value.trim());
}

['change', 'blur'].forEach(evt => {
  els.token.addEventListener(evt, persistInputs);
  els.defaultAgentId.addEventListener(evt, () => {
    const value = els.defaultAgentId.value.trim();
    if (!els.invokeAgentId.value.trim()) els.invokeAgentId.value = value;
    if (!els.taskAgentId.value.trim()) els.taskAgentId.value = value;
    if (!els.chatAgentId.value.trim()) els.chatAgentId.value = value;
    persistInputs();
  });
});


function hex(bytes) {
  return [...bytes].map(b => b.toString(16).padStart(2,'0')).join('');
}

async function hmacSha256Hex(key, msg) {
  const enc = new TextEncoder();
  const keyData = enc.encode(key);
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', cryptoKey, enc.encode(msg));
  return hex(new Uint8Array(sig));
}

function newNonce() {
  const bytes = new Uint8Array(12);
  crypto.getRandomValues(bytes);
  return hex(bytes);
}

async function execSignatureHeaders(method, path, bodyText) {
  const key = (els.execKey.value || '').trim();
  if (!key) {
    // If server enforces exec signature, request will 401. We surface this early.
    throw new Error('缺少 EXEC_SIGNING_KEY：执行类接口需要签名才能调用');
  }
  const ts = Math.floor(Date.now() / 1000);
  const nonce = newNonce();
  const msg = `${ts}.${nonce}.${method}.${path}.${bodyText || ''}`;
  const sig = await hmacSha256Hex(key, msg);
  return {
    'X-Exec-Timestamp': String(ts),
    'X-Exec-Nonce': nonce,
    'X-Exec-Signature': sig,
  };
}

function authHeaders(json=true) {
  const headers = { 'Authorization': 'Bearer ' + els.token.value.trim() };
  if (json) headers['Content-Type'] = 'application/json';
  return headers;
}

function setDot(el, kind) {
  el.className = 'status-dot ' + (kind || '');
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

function safeParseJson(raw, fallbackName) {
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(fallbackName + ' JSON 解析失败：' + error.message);
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function nowText() {
  return new Date().toLocaleString('zh-CN', { hour12: false });
}

function badgeHtml(text, cls='') {
  return `<span class="badge ${cls}">${escapeHtml(text)}</span>`;
}

function updateLogCount(key) {
  const count = state.logCounts[key] || 0;
  const map = {
    remoteSent: els.remoteSentCount,
    remoteRecv: els.remoteRecvCount,
    localSent: els.localSentCount,
    localRecv: els.localRecvCount,
  };
  if (map[key]) map[key].textContent = `${count} 条`;
}

function ensureLogReady(container) {
  if (container.textContent.includes('等待操作') || container.textContent.includes('已清空')) {
    container.innerHTML = '';
  }
}

function trimLogEntries(container) {
  while (container.children.length > MAX_LOG_ENTRIES) {
    container.removeChild(container.lastElementChild);
  }
}

function addPanelEntry(panelKey, title, body={}, options={}) {
  const container = els[panelKey];
  ensureLogReady(container);
  state.logCounts[panelKey] = (state.logCounts[panelKey] || 0) + 1;
  updateLogCount(panelKey);

  const node = document.createElement('div');
  node.className = 'entry';
  const statusLabel = options.pending ? 'PENDING' : (options.ok === false ? 'ERROR' : 'OK');
  const statusColor = options.pending ? '#f59e0b' : (options.ok === false ? '#ef4444' : '#22c55e');
  const badges = [];
  if (options.route === 'relay') badges.push(badgeHtml('relay', 'relay'));
  if (options.inferred) badges.push(badgeHtml('推断', 'inferred'));
  if (options.phase) badges.push(badgeHtml(options.phase));

  let sections = '';
  if (body.summary !== undefined) {
    sections += `<div class="note"><div class="mini">Summary</div><pre>${escapeHtml(String(body.summary))}</pre></div>`;
  }
  if (body.request !== undefined) {
    sections += `<div class="req"><div class="mini">Payload</div><pre>${escapeHtml(formatJson(body.request))}</pre></div>`;
  }
  if (body.response !== undefined) {
    sections += `<div class="res"><div class="mini">Data</div><pre>${escapeHtml(formatJson(body.response))}</pre></div>`;
  }
  if (body.note !== undefined) {
    sections += `<div class="note"><div class="mini">Note</div><pre>${escapeHtml(String(body.note))}</pre></div>`;
  }

  node.innerHTML = `
    <div class="entry-head">
      <div><strong>${escapeHtml(title)}</strong> ${badges.join(' ')}</div>
      <div>${escapeHtml(nowText())} · <span style="color:${statusColor}">${statusLabel}</span></div>
    </div>
    ${sections}
  `;
  container.prepend(node);
  trimLogEntries(container);
}

function clearPanel(panelKey) {
  els[panelKey].innerHTML = '<div class="mini">已清空。</div>';
  state.logCounts[panelKey] = 0;
  updateLogCount(panelKey);
}

function clearAllLogs() {
  clearPanel('remoteSent');
  clearPanel('remoteRecv');
  clearPanel('localSent');
  clearPanel('localRecv');
}

function scrollPanelTop(panelKey) {
  els[panelKey].scrollTop = 0;
}

function scrollPanelBottom(panelKey) {
  els[panelKey].scrollTop = els[panelKey].scrollHeight;
}

function scrollAllLogsTop() {
  ['remoteSent', 'remoteRecv', 'localSent', 'localRecv'].forEach(scrollPanelTop);
}

function scrollAllLogsBottom() {
  ['remoteSent', 'remoteRecv', 'localSent', 'localRecv'].forEach(scrollPanelBottom);
}

function inferLocalLifecycle(meta, responseData, ok=true) {
  if (!meta.hasLocalExecutionHop) {
    return;
  }

  const localTarget = `本地 agent ${meta.agentId || '(unknown agent)'}`;
  const extracted = extractLocalReturnPayload(responseData);
  addPanelEntry('localSent', `${meta.label} · 本地端发送`, {
    summary: `推断：${localTarget} 已向 bridge 返回执行结果或状态。`,
    response: extracted,
    note: meta.localSendNote,
  }, {
    ok,
    route: 'relay',
    inferred: true,
    phase: 'local-tx',
  });
}

function extractLocalReturnPayload(data) {
  if (!data || typeof data !== 'object') return data;
  if (data.result !== undefined) return data.result;
  if (data.data !== undefined) return data.data;
  return data;
}

async function apiRequest(url, options={}, meta={}) {
  const method = (options.method || 'GET').toUpperCase();
  const requestBodyText = options.body;
  let requestBody;
  if (typeof requestBodyText === 'string' && requestBodyText.length) {
    try {
      requestBody = JSON.parse(requestBodyText);
    } catch {
      requestBody = requestBodyText;
    }
  }

  addPanelEntry('remoteSent', `${method} ${url}`, {
    summary: meta.remoteSendSummary || 'console 发起请求到 bridge。',
    request: {
      method,
      path: url,
      headers: meta.logHeaders ? options.headers || {} : undefined,
      body: requestBody,
    },
    note: meta.remoteSendNote,
  }, {
    ok: true,
    route: meta.route || 'relay',
    phase: 'remote-tx',
  });

  if (meta.hasLocalExecutionHop) {
    addPanelEntry('localRecv', `${meta.label} · 本地端接收`, {
      summary: meta.localPendingSummary || `推断：bridge 已将请求转发给本地 agent ${meta.agentId || '(unknown agent)'}，等待其执行。`,
      request: meta.localReceivePayload,
      note: meta.localReceiveNote,
    }, {
      pending: true,
      route: 'relay',
      inferred: true,
      phase: 'local-rx',
    });
  }

  try {
    const response = await fetch(url, options);
    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { raw: text };
    }

    addPanelEntry('remoteRecv', `${method} ${url}`, {
      summary: meta.remoteRecvSummary || 'bridge 返回响应给 console。',
      response: {
        status: response.status,
        ok: response.ok,
        body: data,
      },
      note: meta.remoteRecvNote,
    }, {
      ok: response.ok,
      route: meta.route || 'relay',
      phase: 'remote-rx',
    });

    inferLocalLifecycle(meta, data, response.ok);

    if (!response.ok) {
      const error = new Error('HTTP ' + response.status);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  } catch (error) {
    if (!error.status) {
      addPanelEntry('remoteRecv', `${method} ${url}`, {
        summary: '请求未拿到正常 HTTP 响应。',
        response: { error: error.message },
        note: '可能是网络中断、fetch 抛错或浏览器侧异常。',
      }, {
        ok: false,
        route: meta.route || 'relay',
        phase: 'remote-rx',
      });

      if (meta.hasLocalExecutionHop) {
        addPanelEntry('localRecv', `${meta.label} · 本地端接收`, {
          summary: '未确认本地端是否真的收到请求。',
          request: meta.localReceivePayload,
          note: '因为远程请求在返回前就失败了，这里不再假设本地执行已发生。',
        }, {
          ok: false,
          route: 'relay',
          inferred: true,
          phase: 'local-rx',
        });
      }
    }
    throw error;
  }
}

function renderCapabilities(data) {
  els.capabilityCards.innerHTML = '';

  const relayContract = data && typeof data === 'object' ? (data.relay_contract || {}) : {};
  const actions = state.agents.flatMap(agent => Array.isArray(agent.capabilities) ? agent.capabilities : []);
  const uniqueActions = [...new Set(actions)].sort();
  const allActions = uniqueActions.length ? uniqueActions : ['task_execute', 'local_agent_llm_run'];

  els.invokeAction.innerHTML = allActions.map(name => `<option value="${name}">${name}</option>`).join('');
  if (!allActions.includes(els.invokeAction.value)) {
    els.invokeAction.value = allActions[0];
  }

  const serviceCard = document.createElement('div');
  serviceCard.className = 'card';
  serviceCard.innerHTML = `
    <h3>${escapeHtml(data?.service || 'openclaw-bridge')}</h3>
    <div class="mini">mode: ${escapeHtml(data?.mode || 'transparent-relay')}</div>
    <div class="mini" style="margin-top:8px">requires_agent_id: ${escapeHtml(String(Boolean(relayContract.requires_agent_id)))}</div>
    <div class="mini" style="margin-top:8px">supported_task_types: ${escapeHtml((relayContract.supported_task_types || []).join(', ') || '(none)')}</div>
  `;
  els.capabilityCards.appendChild(serviceCard);

  (relayContract.notes || []).forEach((note, idx) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <h3>relay note ${idx + 1}</h3>
      <div class="mini">${escapeHtml(note || '')}</div>
    `;
    els.capabilityCards.appendChild(card);
  });

  if (!els.capabilityCards.children.length) {
    els.capabilityCards.innerHTML = '<div class="mini">暂无 relay contract 数据。</div>';
  }
}

function renderAgents(agents) {
  state.agents = Array.isArray(agents) ? agents : [];
  els.agentCards.innerHTML = '';
  if (!state.agents.length) {
    els.agentCards.innerHTML = '<div class="mini">当前没有在线 agent。若要走远端 relay 链路，请先启动本地 agent daemon。</div>';
    return;
  }

  state.agents.forEach(agent => {
    const card = document.createElement('div');
    card.className = 'card';
    const caps = Array.isArray(agent.capabilities) ? agent.capabilities.join(', ') : '';
    card.innerHTML = `
      <h3>${escapeHtml(agent.agent_id || '-')}</h3>
      <div class="mini">user: ${escapeHtml(agent.user_id || '-')}</div>
      <div class="mini">device: ${escapeHtml(agent.device_id || '-')}</div>
      <div class="mini">running_tasks: ${escapeHtml(String(agent.running_tasks ?? 0))}</div>
      <div class="mini" style="margin-top:8px">capabilities: ${escapeHtml(caps || '(none)')}</div>
    `;
    card.addEventListener('click', () => {
      els.defaultAgentId.value = agent.agent_id || '';
      els.invokeAgentId.value = agent.agent_id || '';
      els.taskAgentId.value = agent.agent_id || '';
      persistInputs();
    });
    els.agentCards.appendChild(card);
  });
}

async function loadHealth() {
  try {
    const data = await apiRequest('/v1/healthz', {}, {
      label: 'GET /v1/healthz',
      route: 'relay',
      remoteSendSummary: 'console 请求 bridge 健康检查。',
      remoteRecvSummary: 'bridge 返回健康状态。',
      remoteRecvNote: 'healthz 只反映 bridge 服务本身，没有 agent hop。',
      hasLocalExecutionHop: false,
    });
    setDot(els.healthDot, 'ok');
    els.healthStatus.textContent = `${data.status || 'ok'} · ${data.service || ''} · ${data.version || ''}`;
    return data;
  } catch (error) {
    setDot(els.healthDot, 'err');
    els.healthStatus.textContent = error.message;
    throw error;
  }
}

async function loadCapabilities() {
  try {
    const data = await apiRequest('/v1/capabilities', { headers: authHeaders(false) }, {
      label: 'GET /v1/capabilities',
      route: 'relay',
      remoteSendSummary: 'console 请求 bridge relay contract。',
      remoteRecvSummary: 'bridge 返回自己的透明桥接合同与约束。',
      hasLocalExecutionHop: false,
    });
    renderCapabilities(data);
    setDot(els.capDot, 'ok');
    els.capStatus.textContent = `${data.mode || 'transparent-relay'} · ${data.service || '-'} · ${data.version || ''}`;
    return data;
  } catch (error) {
    renderCapabilities([]);
    setDot(els.capDot, error.status === 401 ? 'warn' : 'err');
    els.capStatus.textContent = error.status === 401 ? '鉴权失败：检查 token' : error.message;
    throw error;
  }
}

async function loadAgents() {
  try {
    const data = await apiRequest('/v1/agents', { headers: authHeaders(false) }, {
      label: 'GET /v1/agents',
      route: 'relay',
      remoteSendSummary: 'console 请求在线 agent 列表。',
      remoteRecvSummary: 'bridge 返回当前在线 agent 快照。',
      hasLocalExecutionHop: false,
    });
    renderAgents(data.agents || []);
    setDot(els.agentsDot, (data.count || 0) > 0 ? 'ok' : 'warn');
    els.agentsStatus.textContent = `${data.count || 0} online agent(s)`;
    return data;
  } catch (error) {
    renderAgents([]);
    setDot(els.agentsDot, error.status === 401 ? 'warn' : 'err');
    els.agentsStatus.textContent = error.status === 401 ? '鉴权失败：检查 token' : error.message;
    throw error;
  }
}

async function refreshOverview() {
  persistInputs();
  await loadHealth().catch(() => null);
  await loadCapabilities().catch(() => null);
  await loadAgents().catch(() => null);
}

function normalizedAgentId(raw) {
  const text = (raw || '').trim();
  if (!text) {
    throw new Error('agent_id 是必填的：bridge 只做透明转发，不做本地直连执行');
  }
  return text;
}

function ensureAgentOnline(agentId) {
  const online = state.agents.some(agent => agent.agent_id === agentId);
  if (!online) {
    throw new Error(`目标 agent 不在线：${agentId}。请先刷新 agents，确认本地 agent daemon 已连接。`);
  }
}

function fillInvokePwd() {
  els.invokeAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.invokeAction.value = 'local_command_exec';
  els.invokeTimeout.value = 30;
  els.invokeInput.value = formatJson({ command_id: 'pwd' });
}

function fillInvokeGateway() {
  els.invokeAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.invokeAction.value = 'check_gateway_status';
  els.invokeTimeout.value = 15;
  els.invokeInput.value = formatJson({});
}

function fillInvokeFetch() {
  els.invokeAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.invokeAction.value = 'fetch_url';
  els.invokeTimeout.value = 20;
  els.invokeInput.value = formatJson({ url: 'https://example.com' });
}

function fillTaskReadme() {
  els.taskAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.taskTimeout.value = 180;
  els.taskText.value = '读取 /home/ubuntu/.openclaw/workspace/projects/openclaw-bridge/README.md 并返回内容';
  els.taskContext.value = '{}';
}

function fillTaskBaidu() {
  els.taskAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.taskTimeout.value = 180;
  els.taskText.value = '访问 https://www.baidu.com 并返回页面标题和主要内容';
  els.taskContext.value = '{}';
}

function fillTaskSummarize() {
  els.taskAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.taskTimeout.value = 180;
  els.taskText.value = '把下面 context 里的命令输出整理成 5 行摘要';
  els.taskContext.value = formatJson({
    stdout: 'eth0 UP\ninet 192.168.1.10/24\n...',
    source: 'console-demo'
  });
}

function buildInvokePayload() {
  const agentId = normalizedAgentId(els.invokeAgentId.value);
  ensureAgentOnline(agentId);
  return {
    agent_id: agentId,
    action: els.invokeAction.value,
    input: safeParseJson(els.invokeInput.value, 'MCP input'),
    timeout_sec: Number(els.invokeTimeout.value || 30),
  };
}

function buildTaskPayload() {
  const agentId = normalizedAgentId(els.taskAgentId.value);
  ensureAgentOnline(agentId);
  return {
    agent_id: agentId,
    task: els.taskText.value.trim(),
    context: safeParseJson(els.taskContext.value, 'Task context'),
    timeout_sec: Number(els.taskTimeout.value || 180),
  };
}


function fillChatHello() {
  els.chatAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.chatTimeout.value = 180;
  els.chatInput.value = '你好';
}

function fillChatTrash() {
  els.chatAgentId.value = els.defaultAgentId.value.trim() || 'local-exec-agent';
  els.chatTimeout.value = 180;
  els.chatInput.value = '清空回收站';
}

function ensureChatReady() {
  if (els.chatTranscript.textContent.includes('还没有对话') || els.chatTranscript.textContent.includes('已清空')) {
    els.chatTranscript.innerHTML = '';
  }
}

function addChatBubble(role, text, stateLabel='') {
  ensureChatReady();
  const node = document.createElement('div');
  const roleColor = role === 'remote' ? '#60a5fa' : '#a78bfa';
  const roleName = role === 'remote' ? '远程' : '本地';
  node.className = 'entry';
  node.innerHTML = `
    <div class="entry-head">
      <div><strong style="color:${roleColor}">${roleName}</strong></div>
      <div>${escapeHtml(nowText())}${stateLabel ? ' · ' + escapeHtml(stateLabel) : ''}</div>
    </div>
    <pre>${escapeHtml(String(text || ''))}</pre>
  `;
  els.chatTranscript.prepend(node);
  trimLogEntries(els.chatTranscript);
}

function clearChatTranscript() {
  els.chatTranscript.innerHTML = '<div class="mini">已清空。</div>';
}

function buildChatPayload() {
  const agentId = normalizedAgentId(els.chatAgentId.value);
  ensureAgentOnline(agentId);
  const task = (els.chatInput.value || '').trim();
  if (!task) {
    throw new Error('对话内容不能为空');
  }
  return {
    agent_id: agentId,
    task,
    context: {},
    timeout_sec: Number(els.chatTimeout.value || 180),
  };
}

function extractChatReply(data) {
  if (!data || typeof data !== 'object') return String(data || '');
  const body = data.result?.data?.result?.result || data.result?.data?.result || data.result || data;
  if (typeof body === 'string') return body;
  if (body && typeof body === 'object') {
    if (typeof body.content === 'string' && body.content.trim()) return body.content;
    if (typeof body.error === 'string' && body.error.trim()) return `ERROR: ${body.error}`;
    if (body.data && typeof body.data.content === 'string' && body.data.content.trim()) return body.data.content;
    return JSON.stringify(body, null, 2);
  }
  return JSON.stringify(data, null, 2);
}

async function submitRelayChat() {
  persistInputs();
  let payload;
  try {
    payload = buildChatPayload();
  } catch (error) {
    addChatBubble('remote', error.message, 'ERROR');
    return;
  }

  addChatBubble('remote', payload.task, 'SENT');
  addChatBubble('local', '等待本地 agent 返回…', 'PENDING');

  try {
    const data = await apiRequest('/v1/task/execute', {
      method: 'POST',
      headers: Object.assign(authHeaders(true), await execSignatureHeaders('POST', '/v1/mcp/invoke', JSON.stringify(payload))),
      body: JSON.stringify(payload),
    }, buildTaskMeta(payload));
    addChatBubble('local', extractChatReply(data), data.ok ? 'OK' : 'ERROR');
  } catch (error) {
    const detail = error?.data ? JSON.stringify(error.data, null, 2) : error.message;
    addChatBubble('local', detail, 'ERROR');
  }
}

function copyChatPayload() {
  try {
    copyText(formatJson(buildChatPayload()));
  } catch (error) {
    addPanelEntry('remoteRecv', 'Clipboard chat payload', {
      summary: '无法复制 chat payload。',
      response: { error: error.message },
    }, { ok: false, route: 'relay', phase: 'clipboard' });
  }
}

function loadTemplates() {
  try {
    const raw = localStorage.getItem(TEMPLATE_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    state.templates = Array.isArray(parsed) ? parsed : [];
  } catch {
    state.templates = [];
  }
  renderTemplates();
}

function persistTemplates() {
  localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(state.templates.slice(0, MAX_TEMPLATES)));
}

function renderTemplates() {
  els.templateList.innerHTML = '';
  if (!state.templates.length) {
    els.templateList.innerHTML = '<div class="mini">还没有模板。先填好 MCP 或 Task 表单，再点“保存当前表单为模板”。</div>';
    return;
  }

  state.templates.forEach((tpl, index) => {
    const card = document.createElement('div');
    card.className = 'card';
    const summary = tpl.type === 'mcp'
      ? `${tpl.payload?.action || '-'} · agent=${tpl.payload?.agent_id || '(missing)'}`
      : `${tpl.payload?.task || '-'}\nagent=${tpl.payload?.agent_id || '(missing)'}`;
    card.innerHTML = `
      <h3>${escapeHtml(tpl.name || `template-${index + 1}`)}</h3>
      <div class="mini">type: ${escapeHtml(tpl.type || '-')}</div>
      <div class="mini" style="margin-top:8px">${escapeHtml(summary)}</div>
      <div class="mini" style="margin-top:8px">updated: ${escapeHtml(tpl.updatedAt || '-')}</div>
      <div class="tiny-actions" style="margin-top:10px">
        <button class="secondary" data-action="load">载入</button>
        <button class="secondary" data-action="overwrite">覆写为当前</button>
        <button class="ghost" data-action="delete">删除</button>
      </div>
    `;
    card.querySelector('[data-action="load"]').addEventListener('click', () => applyTemplate(index));
    card.querySelector('[data-action="overwrite"]').addEventListener('click', () => overwriteTemplate(index));
    card.querySelector('[data-action="delete"]').addEventListener('click', () => deleteTemplate(index));
    els.templateList.appendChild(card);
  });
}

function currentTemplateSnapshot(typeOverride=null) {
  const type = typeOverride || els.templateType.value;
  if (type === 'mcp') {
    return { type, payload: buildInvokePayload() };
  }
  return { type: 'task', payload: buildTaskPayload() };
}

function saveCurrentAsTemplate() {
  let snapshot;
  try {
    snapshot = currentTemplateSnapshot();
  } catch (error) {
    addPanelEntry('remoteRecv', '保存模板', {
      summary: '保存模板失败。',
      response: { error: error.message },
    }, { ok: false, route: 'relay', phase: 'template' });
    return;
  }

  const name = (els.templateName.value || '').trim() || `${snapshot.type}-${new Date().toLocaleTimeString('zh-CN', { hour12: false })}`;
  state.templates = state.templates.filter(item => item.name !== name);
  state.templates.unshift({
    name,
    type: snapshot.type,
    payload: snapshot.payload,
    updatedAt: nowText(),
  });
  state.templates = state.templates.slice(0, MAX_TEMPLATES);
  persistTemplates();
  renderTemplates();
  addPanelEntry('remoteRecv', '保存模板', {
    summary: `模板已保存：${name}`,
    response: { name, type: snapshot.type, payload: snapshot.payload },
  }, { ok: true, route: 'relay', phase: 'template' });
}

function applyTemplate(index) {
  const tpl = state.templates[index];
  if (!tpl) return;
  els.templateName.value = tpl.name || '';
  els.templateType.value = tpl.type || 'mcp';

  if (tpl.type === 'mcp') {
    const payload = tpl.payload || {};
    els.invokeAgentId.value = payload.agent_id || '';
    els.invokeAction.value = payload.action || 'local_command_exec';
    els.invokeInput.value = formatJson(payload.input || {});
    els.invokeTimeout.value = Number(payload.timeout_sec || 30);
  } else {
    const payload = tpl.payload || {};
    els.taskAgentId.value = payload.agent_id || '';
    els.taskText.value = payload.task || '';
    els.taskContext.value = formatJson(payload.context || {});
    els.taskTimeout.value = Number(payload.timeout_sec || 180);
  }

  addPanelEntry('remoteRecv', '载入模板', {
    summary: `已回填模板：${tpl.name}`,
    response: tpl,
  }, { ok: true, route: 'relay', phase: 'template' });
}

function overwriteTemplate(index) {
  const existing = state.templates[index];
  if (!existing) return;

  let snapshot;
  try {
    snapshot = currentTemplateSnapshot(existing.type);
  } catch (error) {
    addPanelEntry('remoteRecv', '覆写模板', {
      summary: '覆写模板失败。',
      response: { error: error.message },
    }, { ok: false, route: 'relay', phase: 'template' });
    return;
  }

  state.templates[index] = {
    name: existing.name,
    type: existing.type,
    payload: snapshot.payload,
    updatedAt: nowText(),
  };
  persistTemplates();
  renderTemplates();
  addPanelEntry('remoteRecv', '覆写模板', {
    summary: `已覆写模板：${existing.name}`,
    response: state.templates[index],
  }, { ok: true, route: 'relay', phase: 'template' });
}

function deleteTemplate(index) {
  const existing = state.templates[index];
  if (!existing) return;
  state.templates.splice(index, 1);
  persistTemplates();
  renderTemplates();
  addPanelEntry('remoteRecv', '删除模板', {
    summary: `已删除模板：${existing.name}`,
    response: existing,
  }, { ok: true, route: 'relay', phase: 'template' });
}

function clearTemplates() {
  state.templates = [];
  localStorage.removeItem(TEMPLATE_STORAGE_KEY);
  renderTemplates();
  addPanelEntry('remoteRecv', '清空模板', {
    summary: '最近请求模板已清空。',
    response: { ok: true },
  }, { ok: true, route: 'relay', phase: 'template' });
}

function buildInvokeMeta(payload) {
  return {
    label: 'POST /v1/mcp/invoke',
    route: 'relay',
    hasLocalExecutionHop: true,
    agentId: payload.agent_id,
    remoteSendSummary: `console 提交 action=${payload.action}，bridge 将原样转发给本地 agent。`,
    remoteRecvSummary: 'bridge 返回本地 agent 的执行结果。',
    localPendingSummary: `推断：bridge 已受理该请求，并准备把 action=${payload.action} 转发给本地 agent ${payload.agent_id}。`,
    localReceivePayload: {
      action: payload.action,
      timeout_sec: payload.timeout_sec,
      input: payload.input,
      agent_id: payload.agent_id,
      task_shape: 'task.run',
    },
    localReceiveNote: '现有 API 没有单独暴露 agent 收到 task.run 的实时事件，这里先显示“已转发/待执行”的保守推断。',
    localSendNote: '现有返回体只有聚合结果，没有独立 agent 事件流；这里展示 result 字段或整体回包中的 agent 返回结果。',
  };
}

function buildTaskMeta(payload) {
  return {
    label: 'POST /v1/task/execute',
    route: 'relay',
    hasLocalExecutionHop: true,
    agentId: payload.agent_id,
    remoteSendSummary: 'console 提交自然语言任务，bridge 将原样转发给本地 agent 的 task_execute。',
    remoteRecvSummary: 'bridge 返回本地 agent 处理 task_execute 后的结果。',
    localPendingSummary: `推断：bridge 已受理该任务，并准备把 task_execute 转发给本地 agent ${payload.agent_id}。`,
    localReceivePayload: {
      action: 'task_execute',
      timeout_sec: payload.timeout_sec,
      input: {
        task: payload.task,
        context: payload.context,
        timeout_sec: payload.timeout_sec,
      },
      agent_id: payload.agent_id,
      task_shape: 'task.run',
    },
    localReceiveNote: 'bridge 不理解任务语义。这里仅依据 relay 转发语义，先显示“已转发/待执行”的保守推断。',
    localSendNote: '如果返回体含 result 字段，优先展示它，作为 agent 向 bridge 的回传结果。',
  };
}

async function submitInvoke() {
  persistInputs();
  let payload;
  try {
    payload = buildInvokePayload();
  } catch (error) {
    addPanelEntry('remoteSent', 'POST /v1/mcp/invoke', {
      summary: '请求未发出：payload 构建失败。',
      request: { invalid: true },
      note: error.message,
    }, { ok: false, route: 'relay', phase: 'remote-tx' });
    return;
  }

  try {
    await apiRequest('/v1/mcp/invoke', {
      method: 'POST',
      headers: Object.assign(authHeaders(true), await execSignatureHeaders('POST', '/v1/task/execute', JSON.stringify(payload))),
      body: JSON.stringify(payload),
    }, buildInvokeMeta(payload));
  } catch (error) {
    // 日志已经在 apiRequest 中落盘
  }
}

async function submitTaskExecute() {
  persistInputs();
  let payload;
  try {
    payload = buildTaskPayload();
  } catch (error) {
    addPanelEntry('remoteSent', 'POST /v1/task/execute', {
      summary: '请求未发出：payload 构建失败。',
      request: { invalid: true },
      note: error.message,
    }, { ok: false, route: 'relay', phase: 'remote-tx' });
    return;
  }

  try {
    await apiRequest('/v1/task/execute', {
      method: 'POST',
      headers: Object.assign(authHeaders(true), await execSignatureHeaders('POST', '/v1/task/execute', JSON.stringify(payload))),
      body: JSON.stringify(payload),
    }, buildTaskMeta(payload));
  } catch (error) {
    // 日志已经在 apiRequest 中落盘
  }
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    addPanelEntry('remoteRecv', 'Clipboard', {
      summary: '内容已复制到剪贴板。',
      response: { text },
    }, { ok: true, route: 'relay', phase: 'clipboard' });
  } catch (error) {
    addPanelEntry('remoteRecv', 'Clipboard', {
      summary: '复制失败。',
      response: { error: error.message, text },
    }, { ok: false, route: 'relay', phase: 'clipboard' });
  }
}

function copyInvokePayload() {
  try {
    copyText(formatJson(buildInvokePayload()));
  } catch (error) {
    addPanelEntry('remoteRecv', 'Clipboard invoke payload', {
      summary: '无法复制 invoke payload。',
      response: { error: error.message },
    }, { ok: false, route: 'relay', phase: 'clipboard' });
  }
}

function copyTaskPayload() {
  try {
    copyText(formatJson(buildTaskPayload()));
  } catch (error) {
    addPanelEntry('remoteRecv', 'Clipboard task payload', {
      summary: '无法复制 task payload。',
      response: { error: error.message },
    }, { ok: false, route: 'relay', phase: 'clipboard' });
  }
}

function copyCurlHealth() {
  copyText(`curl -s ${location.origin}/v1/healthz | jq`);
}

function copyCurlAgents() {
  const token = els.token.value.trim();
  copyText(`curl -s -H 'Authorization: Bearer ${token}' ${location.origin}/v1/agents | jq`);
}

window.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
'''


@router.get('/console', response_class=HTMLResponse)
async def console_page() -> str:
    return HTML
