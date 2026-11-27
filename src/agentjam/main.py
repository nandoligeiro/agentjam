import os
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agentjam.modules.agents.public import Agent
from agentjam.modules.tasks.public import TaskService
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.adapters.provider_config import configured_provider
from agentjam.modules.tasks.public import ProviderError

from agentjam.adapters.runtime_sqlite import SQLiteRuntimeStore
from agentjam.modules.runtime.public import Runtime
from agentjam.modules.runtime.api import runtime_router

class AgentInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    instructions: str = Field(default="", max_length=20000)

class TaskInput(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)

def create_app(path: str | None = None):
    app = FastAPI(title="AgentJam", version="0.1.0.dev0")
    store = SQLiteStore(path or os.getenv("AGENTJAM_DB", "agentjam.db"))
    provider_name, provider = configured_provider()
    service = TaskService(store, store, provider)
    app.include_router(runtime_router(Runtime(store, SQLiteRuntimeStore(store), provider)))

    @app.get("/health")
    def health():
        return {"status": "ok", "provider": provider_name}

    @app.post("/agents", status_code=201)
    def create_agent(data: AgentInput):
        agent = Agent(str(uuid4()), data.name, data.instructions)
        store.save_agent(agent)
        return agent

    @app.get("/agents")
    def agents():
        return store.list_agents()

    @app.post("/agents/{agent_id}/tasks", status_code=201)
    def run_task(agent_id: str, data: TaskInput):
        try:
            return service.run(agent_id, data.prompt)
        except ProviderError:
            raise HTTPException(502, "Agent provider execution failed")
        except LookupError:
            raise HTTPException(404, "Agent not found")

    @app.get("/agents/{agent_id}/tasks")
    def tasks(agent_id: str):
        if not store.get_agent(agent_id):
            raise HTTPException(404, "Agent not found")
        return store.list_tasks(agent_id)
    return app

app = create_app()
