import json
import sys

def send(**msg):
    print(json.dumps({"jsonrpc":"2.0", **msg}), flush=True)

for line in sys.stdin:
    msg = json.loads(line)
    method = msg.get("method")
    if method == "initialize":
        send(id=msg["id"], result={"protocolVersion": 1})
    elif method == "session/new":
        assert msg["params"]["mcpServers"] == []
        send(id=msg["id"], result={"sessionId":"s1"})
    elif method == "session/prompt":
        assert msg["params"]["sessionId"] == "s1"
        send(id=90, method="session/request_permission", params={"sessionId":"s1","options":[],"toolCall":{}})
        reply = json.loads(sys.stdin.readline())
        assert reply["result"]["outcome"]["outcome"] == "cancelled"
        for part in ["Hello", " world"]:
            send(method="session/update", params={"sessionId":"s1","update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":part}}})
        send(id=msg["id"], result={"stopReason":"end_turn"})
