#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntu/.openclaw/workspace/projects/openclaw-bridge"
VENV="/tmp/openclaw-bridge-venv"

source "$VENV/bin/activate"
cd "$ROOT"
exec "$VENV/bin/python" -m app.agent.daemon
