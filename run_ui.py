#!/usr/bin/env python3
"""Run Streamlit UI."""
import subprocess, sys
from pathlib import Path
subprocess.run([sys.executable, "-m", "streamlit", "run",
    str(Path(__file__).resolve().parent / "app" / "streamlit_ui.py"),
    "--server.headless", "true"], check=True)
