"""CLI for agent."""

from __future__ import annotations

import argparse
import json

from agent.agent import run_agent
from shared.config import get_org_config_dir


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--org", required=True)
    p.add_argument("message", nargs="+")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    get_org_config_dir(args.org)
    r = run_agent(args.org, " ".join(args.message))
    if args.json:
        print(json.dumps({"answer": r.answer, "tools_called": r.tools_called, "confidence": r.confidence, "escalated": r.escalated}, indent=2))
    else:
        print(f"\n{r.answer}\n")


if __name__ == "__main__":
    main()
