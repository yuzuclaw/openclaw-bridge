#!/usr/bin/env bash
set -euo pipefail

PORT="${BRIDGE_PORT:-8888}"

fuser -k "${PORT}/tcp" 2>/dev/null || true
sleep 1
if ss -ltnp | grep -q ":${PORT}"; then
  echo "WARN: port ${PORT} still listening" >&2
  ss -ltnp | grep ":${PORT}" || true
  exit 1
fi

echo "openclaw-bridge stopped (port ${PORT})"
