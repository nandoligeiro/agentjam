from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

class SkillSelection(BaseModel):
    skill_ids: list[str] = Field(max_length=8)

class MemoryInput(BaseModel):
    text: str = Field(min_length=1,max_length=4000)

def context_router(agents, context):
    router = APIRouter()

    def verify(agent_id):
        if agents.get_agent(agent_id) is None:
            raise HTTPException(404,"Agent not found")

    @router.get("/skills")
    def skills():
        return context.skills.list_skills()

    @router.get("/agents/{agent_id}/skills")
    def selected(agent_id: str):
        verify(agent_id)
        return context.repository.selected_skills(agent_id)

    @router.put("/agents/{agent_id}/skills")
    def select(agent_id: str, data: SkillSelection):
        verify(agent_id)
        try:
            context.select(agent_id,data.skill_ids)
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        return context.repository.selected_skills(agent_id)

    @router.get("/agents/{agent_id}/memory")
    def memories(agent_id: str):
        verify(agent_id)
        return context.repository.list_memory(agent_id)

    @router.post("/agents/{agent_id}/memory", status_code=201)
    def remember(agent_id: str, data: MemoryInput):
        verify(agent_id)
        try:
            return context.remember(agent_id,data.text)
        except ValueError as exc:
            raise HTTPException(422,str(exc))

    @router.delete("/agents/{agent_id}/memory/{memory_id}")
    def forget(agent_id: str, memory_id: str):
        verify(agent_id)
        if not context.repository.delete_memory(agent_id,memory_id):
            raise HTTPException(404,"Memory not found")
        return {"deleted":True}

    return router
