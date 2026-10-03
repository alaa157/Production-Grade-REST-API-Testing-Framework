#!/usr/bin/env bash
set -euo pipefail
# Run Python API tests (full reporting: Phase 20).
# Usage: ./scripts/run_tests.sh

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt

pytest "$@"
