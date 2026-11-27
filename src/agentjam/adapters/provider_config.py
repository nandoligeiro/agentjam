import os
import shlex
from pathlib import Path
from agentjam.adapters.acp import AcpProvider
from agentjam.adapters.mock import MockProvider

def configured_provider():
    name = os.getenv("AGENTJAM_PROVIDER", "mock")
    if name == "mock":
        return name, MockProvider()
    if name != "acp":
        raise ValueError("Unknown AgentJam provider")
    if os.getenv("AGENTJAM_ALLOW_UNSANDBOXED_ACP") != "true":
        raise ValueError("ACP requires explicit acknowledgement of missing OS sandbox")
    workspace = os.environ["AGENTJAM_WORKSPACE"]
    command = tuple(shlex.split(os.getenv("AGENTJAM_ACP_COMMAND", "devin acp")))
    return name, AcpProvider(command, Path(workspace), float(os.getenv("AGENTJAM_ACP_TIMEOUT", "120")))
