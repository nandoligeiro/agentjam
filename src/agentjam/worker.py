"""Foreground worker; run under an approved service supervisor for persistence."""
import logging
import math
import os
import signal
import time
from threading import Event

from agentjam.adapters.provider_config import configured_provider
from agentjam.adapters.runtime_sqlite import SQLiteRuntimeStore
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.modules.runtime.public import Runtime

def main():
    logging.basicConfig(level=logging.INFO)
    name, provider = configured_provider()
    if name != "mock" and os.getenv("AGENTJAM_ALLOW_BACKGROUND_ACP") != "true":
        raise RuntimeError("Background ACP requires separate explicit opt-in")
    timeout = float(os.getenv("AGENTJAM_ACP_TIMEOUT", "120")) if name == "acp" else 120
    if not math.isfinite(timeout) or not 0 < timeout <= 3600:
        raise ValueError("Worker provider timeout must be between 0 and 3600 seconds")
    store = SQLiteStore(os.getenv("AGENTJAM_DB", "agentjam.db"))
    runtime = Runtime(store, SQLiteRuntimeStore(store), provider)
    stop = Event()
    def shutdown(*_):
        stop.set()
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    logging.info("AgentJam worker started (%s)", name)
    while not stop.is_set():
        if not runtime.tick(time.time(), timeout + 60):
            stop.wait(1)
    logging.info("AgentJam worker stopped")

if __name__ == "__main__":
    main()
