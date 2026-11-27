from fastapi.testclient import TestClient
from agentjam.main import create_app

def test_persistence(tmp_path):
    path = str(tmp_path / "test.db")
    with TestClient(create_app(path), base_url="http://127.0.0.1:8000", headers={"Authorization":"Bearer "+"t"*43}) as client:
        agent = client.post("/agents", json={"name":"Reviewer"}).json()
        response = client.post(f"/agents/{agent['id']}/tasks", json={"prompt":"Review"})
        assert response.status_code == 201
        assert response.json()["result"] == "[MOCK] Reviewer: Review"
    with TestClient(create_app(path), base_url="http://127.0.0.1:8000", headers={"Authorization":"Bearer "+"t"*43}) as client:
        assert client.get("/agents").json() == [agent]
        assert len(client.get(f"/agents/{agent['id']}/tasks").json()) == 1
        assert client.post("/agents/missing/tasks", json={"prompt":"x"}).status_code == 404
        assert client.post("/agents", json={"name":""}).status_code == 422
