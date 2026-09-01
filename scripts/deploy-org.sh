#!/bin/bash
set -euo pipefail
ORG_ID="${1:-msme-demo}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/python"

echo "=== Deploying $ORG_ID ==="
pip3 install -q -r "$ROOT/requirements.txt"
python3 -m rag.ingest --org "$ORG_ID"
echo "Done. Run: python3 run_ui.py"
