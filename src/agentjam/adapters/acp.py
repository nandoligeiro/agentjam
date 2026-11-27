"""Minimal ACP v1 stdio adapter. No shell or client-side tool execution."""
import asyncio
import json
import os
from pathlib import Path
from agentjam.modules.agents.public import Agent
from agentjam.modules.tasks.public import ProviderError

class AcpProvider:
    def __init__(self, command: tuple[str, ...], workspace: Path, timeout: float = 120):
        if not command or timeout <= 0:
            raise ValueError("Invalid ACP configuration")
        self.command = command
        self.workspace = workspace.resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError("Workspace must be a directory")
        self.timeout = timeout

    def execute(self, agent: Agent, prompt: str) -> str:
        try:
            return asyncio.run(self._execute(agent, prompt))
        except (OSError, ValueError, TimeoutError, EOFError) as exc:
            raise ProviderError("ACP execution failed") from exc

    async def _execute(self, agent: Agent, prompt: str) -> str:
        process = await asyncio.create_subprocess_exec(
            *self.command, cwd=self.workspace, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
            env={k:v for k,v in os.environ.items() if k != "AGENTJAM_API_TOKEN"},
        )
        chunks: list[str] = []
        session_id = None
        async def send(message):
            process.stdin.write((json.dumps({"jsonrpc": "2.0", **message}) + "\n").encode())
            await process.stdin.drain()

        async def request(request_id, method, params):
            await send({"id": request_id, "method": method, "params": params})
            while True:
                line = await process.stdout.readline()
                if not line:
                    raise EOFError("ACP process closed stdout")
                msg = json.loads(line)
                if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
                    raise ProviderError("Invalid ACP message")
                if "method" in msg:
                    if "id" in msg:
                        if msg["method"] == "session/request_permission":
                            await send({"id": msg["id"], "result": {"outcome": {"outcome": "cancelled"}}})
                        else:
                            await send({"id": msg["id"], "error": {"code": -32601, "message": "Client method unsupported"}})
                    elif msg["method"] == "session/update":
                        params = msg.get("params", {})
                        update = params.get("update", {})
                        if session_id is not None and params.get("sessionId") == session_id and update.get("sessionUpdate") == "agent_message_chunk":
                            content = update.get("content", {})
                            if content.get("type") == "text" and isinstance(content.get("text"), str):
                                chunks.append(content["text"])
                                if sum(map(len, chunks)) > 1_000_000:
                                    raise ProviderError("ACP output limit exceeded")
                    continue
                if msg.get("id") != request_id:
                    raise ProviderError("Unexpected ACP response")
                if "error" in msg or not isinstance(msg.get("result"), dict):
                    raise ProviderError(f"ACP request failed: {method}")
                return msg["result"]
        try:
            async with asyncio.timeout(self.timeout):
                initialized = await request(1, "initialize", {"protocolVersion": 1, "clientCapabilities": {}})
                if initialized.get("protocolVersion") != 1:
                    raise ProviderError("Unsupported ACP protocol version")
                session = await request(2, "session/new", {"cwd": str(self.workspace), "mcpServers": []})
                session_id = session.get("sessionId")
                if not isinstance(session_id, str) or not session_id:
                    raise ProviderError("Missing ACP session ID")
                text = f"Agent instructions:\n{agent.instructions}\n\nTask:\n{prompt}"
                result = await request(3, "session/prompt", {"sessionId": session_id, "prompt": [{"type": "text", "text": text}]})
                if result.get("stopReason") != "end_turn":
                    raise ProviderError("ACP turn did not complete normally")
                return "".join(chunks)
        finally:
            if process.returncode is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.wait_for(process.wait(), 2)
                except TimeoutError:
                    process.kill()
                    await process.wait()
