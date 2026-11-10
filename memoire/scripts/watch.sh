#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/docs"
latexmk -pdf -pvc -synctex=1 -interaction=nonstopmode -halt-on-error -outdir=build main.tex
