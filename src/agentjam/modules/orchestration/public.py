"""Explicit, operator-directed delegation. No model output is executed as a command."""
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4
from agentjam.modules.agents.public import AgentRepository
from agentjam.modules.runtime.public import Job

MAX_DEPTH = 3
MAX_CHILDREN = 5
MAX_DESCENDANTS = 20

@dataclass(frozen=True)
class Delegation:
    job_id: str
    parent_job_id: str
    source_agent_id: str
    target_agent_id: str
    depth: int

class DelegationRepository(Protocol):
    def delegate(self, parent_id: str, source_id: str, job: Job) -> Delegation: ...
    def list_delegations(self, agent_id: str) -> list[Delegation]: ...

class Orchestration:
    def __init__(self, agents: AgentRepository, repository: DelegationRepository):
        self.agents, self.repository = agents, repository

    def delegate(self, source_id: str, parent_id: str, target_id: str, prompt: str, now: float) -> Delegation:
        if self.agents.get_agent(source_id) is None or self.agents.get_agent(target_id) is None:
            raise LookupError("Agent not found")
        if source_id == target_id:
            raise ValueError("Cannot delegate to the same agent")
        if not prompt.strip() or len(prompt) > 20000:
            raise ValueError("Invalid task prompt")
        job = Job(str(uuid4()), target_id, prompt.strip(), "queued", now)
        return self.repository.delegate(parent_id, source_id, job)
