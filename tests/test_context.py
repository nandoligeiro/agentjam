from pathlib import Path
from fastapi.testclient import TestClient
from agentjam.main import create_app
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.context_config import configured_context
from agentjam.adapters.mock import MockProvider
from agentjam.adapters.runtime_sqlite import SQLiteRuntimeStore
from agentjam.modules.runtime.public import Runtime
from agentjam.modules.agents.public import Agent

def test_context_api_and_worker(tmp_path,monkeypatch):
    root=tmp_path/"skills"
    root.mkdir()
    (root/"SKILL.md").write_text("Use domain boundaries",encoding="utf-8")
    monkeypatch.setenv("AGENTJAM_SKILLS_PATHS",str(root))
    path=str(tmp_path/"db.sqlite")
    with TestClient(create_app(path)) as client:
        a=client.post("/agents",json={"name":"A"}).json()["id"]
        b=client.post("/agents",json={"name":"B"}).json()["id"]
        skill=client.get("/skills").json()[0]["id"]
        assert client.put(f"/agents/{a}/skills",json={"skill_ids":[skill]}).status_code==200
        memory=client.post(f"/agents/{a}/memory",json={"text":"Prefer explicit contracts"}).json()
        assert client.delete(f"/agents/{b}/memory/{memory['id']}").status_code==404
        result=client.post(f"/agents/{a}/tasks",json={"prompt":"Review"}).json()
        assert "Use domain boundaries" in result["result"]
        assert "Prefer explicit contracts" in result["result"]
        assert result["prompt"]=="Review"
        assert client.post(f"/agents/{b}/tasks",json={"prompt":"Review"}).json()["result"]=="[MOCK] B: Review"
    store=SQLiteStore(path)
    context,provider=configured_context(store,MockProvider())
    runtime=Runtime(store,SQLiteRuntimeStore(store),provider)
    runtime.enqueue(a,"Background review",0)
    assert runtime.tick(1,60)
    assert "Prefer explicit contracts" in store.list_tasks(a)[-1].result

def test_missing_skill_fails_closed(tmp_path,monkeypatch):
    root=tmp_path/"skills"
    root.mkdir()
    file=root/"SKILL.md"
    file.write_text("sample")
    monkeypatch.setenv("AGENTJAM_SKILLS_PATHS",str(root))
    with TestClient(create_app(str(tmp_path/"db"))) as client:
        a=client.post("/agents",json={"name":"A"}).json()["id"]
        sid=client.get("/skills").json()[0]["id"]
        client.put(f"/agents/{a}/skills",json={"skill_ids":[sid]})
        file.unlink()
        assert client.post(f"/agents/{a}/tasks",json={"prompt":"Review"}).status_code==502

def test_symlink_skipped(tmp_path):
    from agentjam.adapters.skills_filesystem import FilesystemSkillsProvider
    root=tmp_path/"skills"
    root.mkdir()
    outside=tmp_path/"outside.md"
    outside.write_text("private")
    import pytest
    try:
        (root/"SKILL.md").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks unavailable")
    assert FilesystemSkillsProvider((root,)).list_skills()==[]
