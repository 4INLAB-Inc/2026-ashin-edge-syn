#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

REQUIRED_PYTHON="3.8.10"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: Python is not installed or not found: $PYTHON_BIN"
  exit 1
fi

CURRENT_PYTHON="$($PYTHON_BIN - <<'PY'
import platform
print(platform.python_version())
PY
)"

if [ "$CURRENT_PYTHON" != "$REQUIRED_PYTHON" ]; then
  echo "ERROR: Python $REQUIRED_PYTHON is required for this project."
  echo "Current Python version: $CURRENT_PYTHON"
  echo ""
  echo "Recommended:"
  echo "  conda env create -f environment.yml"
  echo "  conda activate predictive-maintenance"
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements/dev.txt

python scripts/check_env.py --mode dev

echo ""
echo "Development environment is ready."
echo "Activate it with:"
echo "source .venv/bin/activate"