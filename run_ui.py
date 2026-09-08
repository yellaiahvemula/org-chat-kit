#!/usr/bin/env python3
"""Run legacy Streamlit UI."""
import subprocess
import sys
from pathlib import Path

subprocess.run(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(Path(__file__).resolve().parent / "apps" / "chat-api" / "streamlit_ui.py"),
        "--server.headless",
        "true",
    ],
    check=True,
)
