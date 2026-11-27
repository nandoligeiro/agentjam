"""Independent local tool runner. Never constructs or calls an LLM provider."""
import argparse
import json
import os
import time
from dataclasses import asdict
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.tool_config import configured_registry

def main():
    parser = argparse.ArgumentParser(description="Run a configured deterministic tool")
    parser.add_argument("--tool",default="mock.alarm-count")
    parser.add_argument("--interval",type=int,default=0,help="0 for one run; minimum 300 seconds for recurring AWS queries")
    args = parser.parse_args()
    if args.interval != 0 and not 300 <= args.interval <= 86400:
        parser.error("Interval must be 0 or between 300 and 86400 seconds")
    registry = configured_registry(SQLiteStore(os.getenv("AGENTJAM_DB","agentjam.db")))
    if args.tool not in registry.ids():
        parser.error("Unknown or disabled tool")
    try:
        while True:
            observation = registry.run(args.tool)
            print(json.dumps(asdict(observation)),flush=True)
            # Stop recurring execution on any failure; operator must review and restart.
            if observation.status == "error":
                return 1
            if not args.interval:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
