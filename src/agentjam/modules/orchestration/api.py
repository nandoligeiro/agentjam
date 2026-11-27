import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from agentjam.modules.orchestration.public import Orchestration

class DelegateInput(BaseModel):
    parent_job_id: str = Field(min_length=1,max_length=128)
    target_agent_id: str = Field(min_length=1,max_length=128)
    prompt: str = Field(min_length=1,max_length=20000)

def orchestration_router(service: Orchestration):
    router = APIRouter(prefix="/agents/{agent_id}/delegations")

    @router.post("",status_code=202)
    def delegate(agent_id: str, data: DelegateInput):
        try:
            return service.delegate(agent_id,data.parent_job_id,data.target_agent_id,data.prompt,time.time())
        except LookupError as exc:
            raise HTTPException(404,str(exc))
        except ValueError as exc:
            raise HTTPException(409,str(exc))

    @router.get("")
    def list_delegations(agent_id: str):
        if service.agents.get_agent(agent_id) is None:
            raise HTTPException(404,"Agent not found")
        return service.repository.list_delegations(agent_id)

    return router
