#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <report|memoire>" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_NAME="$1"
SOURCE_FILE="$ROOT_DIR/templates/$TEMPLATE_NAME/main.tex"
TARGET_FILE="$ROOT_DIR/docs/main.tex"

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Template introuvable: $TEMPLATE_NAME" >&2
  exit 1
fi

cp "$SOURCE_FILE" "$TARGET_FILE"
echo "Template '$TEMPLATE_NAME' applique sur docs/main.tex"
