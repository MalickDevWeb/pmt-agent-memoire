#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <source> <start_line> <end_line> <output_png>" >&2
  exit 1
fi

SRC="$1"
START="$2"
END="$3"
OUT="$4"

TMP_FILE="$(mktemp)"
mkdir -p "$(dirname "$OUT")"
sed -n "${START},${END}p" "$SRC" > "$TMP_FILE"

silicon "$TMP_FILE" \
  --output "$OUT" \
  --theme "Monokai Extended" \
  --font "Fira Code=16" \
  --line-number

rm -f "$TMP_FILE"
echo "Capture generee: $OUT"
