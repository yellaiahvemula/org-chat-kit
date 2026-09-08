#!/usr/bin/env python3
"""Run FastAPI chat API server."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "apps" / "chat-api"))
sys.path.insert(0, str(ROOT / "packages" / "chat-core"))

if __name__ == "__main__":
    from api import main

    main()
