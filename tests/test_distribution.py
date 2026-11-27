import pytest
from fastapi.testclient import TestClient
from agentjam.main import create_app
from agentjam.adapters.distribution_config import configured_distribution
from agentjam.adapters.provider_config import configured_provider
from agentjam.adapters.context_config import configured_context
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.mock import MockProvider

MANIFEST = """
apiVersion: agentjam/v1alpha1
kind: Distribution
metadata:
  name: example
spec:
  branding:
    name: Example Workspace
    initials: EX
    primaryColor: "#336699"
  provider:
    type: mock
  skills:
    sources: [skills]
"""

def test_distribution_metadata_and_skills(tmp_path,monkeypatch):
    manifest=tmp_path/"distribution.yaml"
    manifest.write_text(MANIFEST)
    root=tmp_path/"skills"
    root.mkdir()
    (root/"SKILL.md").write_text("Example skill")
    monkeypatch.setenv("AGENTJAM_DISTRIBUTION",str(manifest))
    monkeypatch.delenv("AGENTJAM_SKILLS_PATHS",raising=False)
    with TestClient(create_app(str(tmp_path/"test.db")), base_url="http://127.0.0.1:8000", headers={"Authorization":"Bearer "+"t"*43}) as client:
        info=client.get("/distribution").json()
        assert info["branding"]["name"]=="Example Workspace"
        assert "skills" not in info
        assert client.get("/skills").json()[0]["name"]=="skills"
    monkeypatch.setenv("AGENTJAM_SKILLS_PATHS","")
    context,_=configured_context(SQLiteStore(str(tmp_path/"worker.db")),MockProvider(),configured_distribution())
    assert context.skills.list_skills()==[]

def test_manifest_never_grants_acp_permissions(tmp_path,monkeypatch):
    manifest=tmp_path/"distribution.yaml"
    manifest.write_text(MANIFEST.replace("type: mock","type: acp"))
    monkeypatch.setenv("AGENTJAM_DISTRIBUTION",str(manifest))
    monkeypatch.delenv("AGENTJAM_PROVIDER",raising=False)
    monkeypatch.delenv("AGENTJAM_ALLOW_UNSANDBOXED_ACP",raising=False)
    with pytest.raises(ValueError):
        configured_provider(configured_distribution())
    monkeypatch.setenv("AGENTJAM_PROVIDER","mock")
    assert configured_provider(configured_distribution())[0]=="mock"

def test_unknown_manifest_fields_rejected(tmp_path,monkeypatch):
    manifest=tmp_path/"distribution.yaml"
    manifest.write_text(MANIFEST+"  unauthorized: true\n")
    monkeypatch.setenv("AGENTJAM_DISTRIBUTION",str(manifest))
    with pytest.raises(ValueError):
        configured_distribution()
