#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntu/.openclaw/workspace/projects/openclaw-bridge"
VENV="/tmp/openclaw-bridge-venv"
HOST="${BRIDGE_HOST:-0.0.0.0}"
PORT="${BRIDGE_PORT:-8888}"

mkdir -p /tmp
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -q -r "$ROOT/requirements.txt"
pkill -f "uvicorn app.main:app --host ${HOST} --port ${PORT}" || true
fuser -k "${PORT}/tcp" 2>/dev/null || true
nohup "$VENV/bin/python" -m uvicorn app.main:app --host "$HOST" --port "$PORT" > /tmp/openclaw-bridge.log 2>&1 &
echo "started on http://${HOST}:${PORT}"
