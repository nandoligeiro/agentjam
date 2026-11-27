from fastapi.testclient import TestClient
from agentjam.main import create_app
from agentjam.adapters.provider_config import configured_provider
from agentjam.adapters.local_security import configured_token
import pytest

TOKEN = "t"*43

def test_api_auth_and_origin(tmp_path,monkeypatch):
    monkeypatch.setenv("AGENTJAM_API_TOKEN",TOKEN)
    with TestClient(create_app(str(tmp_path/"db")),base_url="http://127.0.0.1:8000") as client:
        assert client.get("/health").status_code==401
        assert client.get("/health",headers={"Authorization":"Bearer wrong"}).status_code==401
        headers={"Authorization":"Bearer "+TOKEN}
        assert client.get("/health",headers=headers).status_code==200
        assert client.get("/tools/observations",headers=headers).headers["cache-control"]=="no-store"
        assert client.get("/agents",headers={**headers,"Origin":"https://evil.example"}).status_code==403
        assert client.get("/agents",headers={**headers,"Host":"evil.example"}).status_code==403
        assert client.get("/agents",headers={**headers,"Sec-Fetch-Site":"cross-site"}).status_code==403
        assert client.get("/health",headers={**headers,"Origin":"http://127.0.0.1:5173"}).status_code==200

def test_missing_token_locks_api(tmp_path,monkeypatch):
    monkeypatch.delenv("AGENTJAM_API_TOKEN",raising=False)
    with TestClient(create_app(str(tmp_path/"db")),base_url="http://127.0.0.1:8000") as client:
        assert client.get("/health").status_code==401

def test_pre_blocks_acp(monkeypatch):
    monkeypatch.setenv("AGENTJAM_POC_MODE","pre")
    monkeypatch.setenv("AGENTJAM_PROVIDER","acp")
    monkeypatch.setenv("AGENTJAM_ALLOW_UNSANDBOXED_ACP","true")
    with pytest.raises(ValueError,match="PRE"):
        configured_provider()

def test_short_token_rejected(monkeypatch):
    monkeypatch.setenv("AGENTJAM_API_TOKEN","password")
    with pytest.raises(ValueError):
        configured_token()
