#!/usr/bin/env python3
"""Run API server."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from app.api import main
    main()
