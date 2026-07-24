#!/usr/bin/env bash
set -euo pipefail

if command -v lsof >/dev/null 2>&1; then
  pids=$(lsof -ti tcp:8000 || true)
  if [ -n "${pids}" ]; then
    kill -9 ${pids}
  fi
fi
