import pytest

@pytest.fixture(autouse=True)
def local_api_token(monkeypatch):
    monkeypatch.setenv("AGENTJAM_API_TOKEN","t"*43)
    monkeypatch.setenv("AGENTJAM_POC_MODE","local")
