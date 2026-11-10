#!/usr/bin/env bash
set -euo pipefail

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $cmd"
  else
    echo "[KO] $cmd"
  fi
}

echo "== Verification environnement Documentation_des_projet =="
check_cmd docker
check_cmd code
check_cmd latexmk
check_cmd python3
check_cmd silicon
check_cmd wmctrl
check_cmd xdotool
check_cmd xwininfo

echo "DISPLAY=${DISPLAY:-non-defini}"
