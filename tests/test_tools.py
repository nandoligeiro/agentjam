import json
import subprocess
from pathlib import Path
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.tool_config import configured_registry
from agentjam.adapters.tool_aws_cli import AwsAlarmTool
from agentjam.adapters.tool_sqlite import SQLiteObservationStore
from agentjam.modules.tools.public import Registry
from fastapi.testclient import TestClient
from agentjam.main import create_app
import pytest

def test_mock_and_history(tmp_path,monkeypatch):
    monkeypatch.delenv("AGENTJAM_ENABLE_AWS_TOOL",raising=False)
    path=str(tmp_path/"tools.db")
    registry=configured_registry(SQLiteStore(path))
    assert registry.ids()==["mock.alarm-count"]
    assert registry.run("mock.alarm-count").status=="clear"
    with pytest.raises(LookupError):
        registry.run("aws.cloudwatch.alarm-count")
    with TestClient(create_app(path)) as client:
        assert client.get("/tools/observations").json()[0]["alarm_count"]==0
        assert client.post("/tools/observations").status_code==405

def test_fixed_aws_query_and_sanitized_result(tmp_path,monkeypatch):
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY","never-pass-this")
    def fake(args,**kwargs):
        assert args[1:3]==["cloudwatch","describe-alarms"]
        assert kwargs["shell"] is False
        assert kwargs["timeout"]==30
        assert "AWS_SECRET_ACCESS_KEY" not in kwargs["env"]
        assert "--profile" in args
        return subprocess.CompletedProcess(args,0,b'{"metric":2,"composite":1}',b"")
    monkeypatch.setattr(subprocess,"run",fake)
    tool=AwsAlarmTool(Path("/trusted/aws"),"test","us-east-1")
    registry=Registry([tool],SQLiteObservationStore(SQLiteStore(str(tmp_path/"db"))))
    result=registry.run(tool.id)
    assert result.alarm_count==3
    assert result.status=="attention"

def test_failure_does_not_persist_stderr(tmp_path,monkeypatch):
    monkeypatch.setattr(subprocess,"run",lambda *a,**k: subprocess.CompletedProcess([],1,b"",b"private output"))
    tool=AwsAlarmTool(Path("/trusted/aws"),"test","us-east-1")
    registry=Registry([tool],SQLiteObservationStore(SQLiteStore(str(tmp_path/"db"))))
    result=registry.run(tool.id)
    assert result.status=="error"
    assert result.alarm_count is None
    assert "private" not in json.dumps(result.__dict__)
