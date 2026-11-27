from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from agentjam.main import create_app
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.runtime_sqlite import SQLiteRuntimeStore
from agentjam.adapters.mock import MockProvider
from agentjam.modules.agents.public import Agent
from agentjam.modules.runtime.public import Runtime

def setup(tmp_path):
    store=SQLiteStore(str(tmp_path/"runtime.db"))
    store.save_agent(Agent("a","Test",""))
    repo=SQLiteRuntimeStore(store)
    return store,repo,Runtime(store,repo,MockProvider())

def test_durable_queue_and_result(tmp_path):
    store,repo,runtime=setup(tmp_path)
    job=runtime.enqueue("a","hello",10)
    assert not runtime.tick(9,60)
    recreated=SQLiteRuntimeStore(SQLiteStore(store.path))
    assert Runtime(store,recreated,MockProvider()).tick(10,60)
    assert recreated.list_jobs("a")[0].status=="succeeded"
    assert store.list_tasks("a")[0].id==job.id

def test_atomic_claim_and_interruption(tmp_path):
    store,repo,runtime=setup(tmp_path)
    runtime.enqueue("a","first",0)
    runtime.enqueue("a","second",0)
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims=list(pool.map(lambda _:repo.claim(1,20),range(2)))
    assert sum(j is not None for j in claims)==1
    job=next(j for j in claims if j)
    assert repo.interrupt_expired(19)==0
    assert repo.interrupt_expired(20)==1
    assert not repo.finish(job.id,"late",None)
    assert repo.list_jobs("a")[0].status=="interrupted"
    assert runtime.tick(21,60)
    assert len(store.list_tasks("a"))==1

def test_schedule_coalescing_and_disable(tmp_path):
    _,repo,runtime=setup(tmp_path)
    schedule=runtime.schedule("a","recurring",60,0)
    assert repo.materialize_due(59)==0
    assert repo.materialize_due(181)==1
    assert repo.list_schedules("a")[0].next_at==240
    assert repo.materialize_due(241)==0
    assert repo.disable_schedule("a",schedule.id)
    assert repo.materialize_due(600)==0
    assert len(repo.list_jobs("a"))==1

def test_api(tmp_path):
    with TestClient(create_app(str(tmp_path/"api.db"))) as client:
        agent=client.post("/agents",json={"name":"Test"}).json()
        path=f"/agents/{agent['id']}"
        assert client.post(path+"/jobs",json={"prompt":"hello"}).status_code==202
        assert client.get(path+"/jobs").json()[0]["status"]=="queued"
        assert client.post(path+"/schedules",json={"prompt":"hello","interval_seconds":59}).status_code==422
        schedule=client.post(path+"/schedules",json={"prompt":"hello","interval_seconds":60}).json()
        assert client.delete(path+"/schedules/"+schedule["id"]).status_code==200
        assert client.get(path+"/schedules").json()[0]["enabled"] is False
