#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/docs"
latexmk -pdf -synctex=1 -interaction=nonstopmode -halt-on-error -outdir=build main.tex
ln -sfn "$ROOT_DIR/docs/build/main.pdf" "$ROOT_DIR/docs/main.pdf"
