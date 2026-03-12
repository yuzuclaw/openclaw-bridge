#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntu/.openclaw/workspace/projects/openclaw-bridge"
VENV="/tmp/openclaw-bridge-venv"
INFRA="/home/ubuntu/.openclaw/workspace/secrets/INFRA.md"
HOST="${BRIDGE_HOST:-0.0.0.0}"
PORT="${BRIDGE_PORT:-8888}"

# Extract KEY=VALUE lines from INFRA.md (markdown) without sourcing it.
get_key() {
  local key="$1"
  grep -E "^${key}=" "$INFRA" | tail -n1 | cut -d= -f2-
}

export BRIDGE_API_KEY="${BRIDGE_API_KEY:-$(get_key BRIDGE_API_KEY)}"
export EXEC_SIGNING_KEY="${EXEC_SIGNING_KEY:-$(get_key EXEC_SIGNING_KEY)}"
export CONSOLE_BASIC_USER="${CONSOLE_BASIC_USER:-$(get_key CONSOLE_BASIC_USER)}"
export CONSOLE_BASIC_PASS="${CONSOLE_BASIC_PASS:-$(get_key CONSOLE_BASIC_PASS)}"

if [[ -z "${BRIDGE_API_KEY:-}" ]]; then
  echo "ERROR: BRIDGE_API_KEY is empty (set env or add BRIDGE_API_KEY=... to $INFRA)" >&2
  exit 1
fi
if [[ -z "${EXEC_SIGNING_KEY:-}" ]]; then
  echo "ERROR: EXEC_SIGNING_KEY is empty (set env or add EXEC_SIGNING_KEY=... to $INFRA)" >&2
  exit 1
fi
if [[ -z "${CONSOLE_BASIC_PASS:-}" ]]; then
  echo "ERROR: CONSOLE_BASIC_PASS is empty (set env or add CONSOLE_BASIC_PASS=... to $INFRA)" >&2
  exit 1
fi

mkdir -p /tmp

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q -r "$ROOT/requirements.txt"

# Stop existing listener on port
fuser -k "${PORT}/tcp" 2>/dev/null || true

cd "$ROOT"
nohup python -m uvicorn app.main:app --host "$HOST" --port "$PORT" > /tmp/openclaw-bridge.log 2>&1 &

echo "openclaw-bridge started"
echo "- http://127.0.0.1:${PORT}/console (BasicAuth)"
echo "- http://${HOST}:${PORT}/v1/healthz"
