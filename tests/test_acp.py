import sys
from pathlib import Path
import pytest
from agentjam.adapters.acp import AcpProvider
from agentjam.adapters.provider_config import configured_provider
from agentjam.modules.agents.public import Agent
from agentjam.modules.tasks.public import ProviderError

def test_acp_turn(tmp_path):
    fake = Path(__file__).with_name("fake_acp.py").resolve()
    provider = AcpProvider((sys.executable, str(fake)), tmp_path, 5)
    assert provider.execute(Agent("1","Test","Be helpful"),"Say hello") == "Hello world"

def test_acp_timeout(tmp_path):
    provider = AcpProvider((sys.executable,"-c","import time; time.sleep(30)"), tmp_path, 0.2)
    with pytest.raises(ProviderError):
        provider.execute(Agent("1","Test",""),"Hello")

def test_acp_opt_in(monkeypatch):
    monkeypatch.setenv("AGENTJAM_PROVIDER","acp")
    monkeypatch.delenv("AGENTJAM_ALLOW_UNSANDBOXED_ACP",raising=False)
    with pytest.raises(ValueError):
        configured_provider()
