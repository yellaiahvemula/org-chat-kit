#!/usr/bin/env python3
"""Run API server."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.api import main
main()
