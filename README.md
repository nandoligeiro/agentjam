# AgentJam
Local-first modular workspace for persistent AI agents.

## Status
Early walking skeleton: persistent agents and task history, manual execution through a mock provider. An experimental ACP v1 adapter is available. Scheduled execution, real isolation are not implemented yet; an initial web workspace is available. Do not connect sensitive repositories.

## Run
```sh
uv sync --extra dev
uv run uvicorn agentjam.main:app --host 127.0.0.1 --port 8000
uv run pytest
```
Open http://127.0.0.1:8000/docs. Create an agent, then submit a task. Results are simulated by default. The database defaults to `agentjam.db`.

## Web workspace

Start the backend as above, then in a second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Create an agent and run tasks. The timeline displays persisted independent task results, not conversational context. Mock remains the default. Node.js 22 recommended. Run `npm test` and `npm run build` for checks. Development and preview are loopback-only; do not expose the unauthenticated API or UI.

## Experimental ACP provider (POSIX shell)
Only use in an isolated disposable environment. The child process is not sandboxed. Do not expose this unauthenticated API to a network or connect sensitive repositories.

```sh
export AGENTJAM_PROVIDER=acp
export AGENTJAM_ALLOW_UNSANDBOXED_ACP=true
export AGENTJAM_WORKSPACE=/absolute/path/to/disposable-workspace
export AGENTJAM_ACP_COMMAND="devin acp"
uv run uvicorn agentjam.main:app --host 127.0.0.1 --port 8000
```

Devin must already be installed and authenticated in the approved test environment. Real Devin compatibility is not yet validated. Each task starts a new ACP v1 session; text is collected before returning. Permission requests are cancelled, not automatically approved. See [ADR 0001](docs/adr/0001-acp-provider.md).

## Architecture
Modular monolith with explicit module contracts; provider and persistence adapters are replaceable. Distributions supply branding, skills and policies separately. No corporate data belongs upstream.

## Roadmap
1. ACP handshake, capability negotiation, permission handling and streaming.
2. Durable task queue, scheduler and recovery.
3. Workspace isolation, approval gates and audit.
4. Skills registry, persistent context and web workspace.
5. Versioned distribution packaging.

License: Apache-2.0.
