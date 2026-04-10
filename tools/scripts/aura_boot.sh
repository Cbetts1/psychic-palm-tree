#!/usr/bin/env bash
set -e

echo "AURa Boot — starting..."

if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
  echo "Python is required to run AURa."
  exit 1
fi

PYTHON_BIN=$(command -v python3 || command -v python)

$PYTHON_BIN -m core.runtime.vhost
