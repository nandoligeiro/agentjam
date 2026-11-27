from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from agentjam.main import create_app
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.runtime_sqlite import SQLiteRuntimeStore
from agentjam.adapters.orchestration_sqlite import SQLiteDelegationStore
from agentjam.adapters.mock import MockProvider
from agentjam.modules.runtime.public import Runtime
from agentjam.modules.orchestration.public import Orchestration
from agentjam.modules.agents.public import Agent
import pytest

def setup(tmp_path):
    store = SQLiteStore(str(tmp_path/"test.db"))
    for name in "abcde":
        store.save_agent(Agent(name,name,""))
    jobs = SQLiteRuntimeStore(store)
    runtime = Runtime(store,jobs,MockProvider())
    service = Orchestration(store,SQLiteDelegationStore(store))
    root = runtime.enqueue("a","root",0)
    return runtime,service,root

def test_lineage_and_cycle(tmp_path):
    runtime,service,root = setup(tmp_path)
    with pytest.raises(ValueError):
        service.delegate("a",root.id,"b","child",1)
    assert runtime.tick(1,60)
    child = service.delegate("a",root.id,"b","child",2)
    assert child.depth == 1
    assert runtime.tick(2,60)
    with pytest.raises(ValueError):
        service.delegate("b",child.job_id,"a","cycle",3)
    grandchild = service.delegate("b",child.job_id,"c","grandchild",3)
    assert grandchild.depth == 2
    assert runtime.tick(3,60)
    third = service.delegate("c",grandchild.job_id,"d","third",4)
    assert runtime.tick(4,60)
    with pytest.raises(ValueError):
        service.delegate("d",third.job_id,"e","too deep",5)
    assert len(service.repository.list_delegations("b")) == 2

def test_atomic_fanout(tmp_path):
    runtime,service,root = setup(tmp_path)
    runtime.tick(1,60)
    def submit(i):
        try:
            return service.delegate("a",root.id,"b",str(i),2)
        except ValueError:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(submit,range(8)))
    assert sum(r is not None for r in results) == 5
    assert len(runtime.repository.list_jobs("b")) == 5

def test_api_and_ownership(tmp_path):
    path=str(tmp_path/"api.db")
    with TestClient(create_app(path)) as client:
        a=client.post("/agents",json={"name":"A"}).json()["id"]
        b=client.post("/agents",json={"name":"B"}).json()["id"]
        job=client.post(f"/agents/{a}/jobs",json={"prompt":"root"}).json()
        store=SQLiteStore(path)
        Runtime(store,SQLiteRuntimeStore(store),MockProvider()).tick(job["due_at"]+1,60)
        data={"parent_job_id":job["id"],"target_agent_id":b,"prompt":"child"}
        assert client.post(f"/agents/{b}/delegations",json={**data,"target_agent_id":a}).status_code==404
        result=client.post(f"/agents/{a}/delegations",json=data)
        assert result.status_code==202
        assert client.get(f"/agents/{b}/delegations").json()[0]["job_id"]==result.json()["job_id"]
