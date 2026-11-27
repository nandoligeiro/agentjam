import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from agentjam.modules.runtime.public import Runtime

class JobInput(BaseModel):
    prompt: str = Field(min_length=1,max_length=20000)
    delay_seconds: int = Field(default=0,ge=0,le=2592000)

class ScheduleInput(BaseModel):
    prompt: str = Field(min_length=1,max_length=20000)
    interval_seconds: int = Field(ge=60,le=2592000)

def runtime_router(runtime: Runtime):
    router = APIRouter(prefix="/agents/{agent_id}")

    def verify(agent_id):
        if runtime.agents.get_agent(agent_id) is None:
            raise HTTPException(404,"Agent not found")

    @router.post("/jobs", status_code=202)
    def enqueue(agent_id: str, data: JobInput):
        verify(agent_id)
        return runtime.enqueue(agent_id,data.prompt,time.time()+data.delay_seconds)

    @router.get("/jobs")
    def jobs(agent_id: str):
        verify(agent_id)
        return runtime.repository.list_jobs(agent_id)

    @router.post("/schedules", status_code=201)
    def schedule(agent_id: str, data: ScheduleInput):
        verify(agent_id)
        return runtime.schedule(agent_id,data.prompt,data.interval_seconds,time.time())

    @router.get("/schedules")
    def schedules(agent_id: str):
        verify(agent_id)
        return runtime.repository.list_schedules(agent_id)

    @router.delete("/schedules/{schedule_id}")
    def disable(agent_id: str, schedule_id: str):
        verify(agent_id)
        if not runtime.repository.disable_schedule(agent_id,schedule_id):
            raise HTTPException(404,"Schedule not found")
        return {"enabled":False}

    return router
