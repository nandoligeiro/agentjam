from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from agentjam.modules.agents.public import AgentRepository
from agentjam.modules.tasks.public import Provider

@dataclass(frozen=True)
class Job:
    id: str
    agent_id: str
    prompt: str
    status: str
    due_at: float
    result: str | None = None
    error: str | None = None

@dataclass(frozen=True)
class Schedule:
    id: str
    agent_id: str
    prompt: str
    interval_seconds: int
    next_at: float
    enabled: bool = True

class RuntimeRepository(Protocol):
    def enqueue(self, job: Job) -> None: ...
    def list_jobs(self, agent_id: str) -> list[Job]: ...
    def claim(self, now: float, deadline: float) -> Job | None: ...
    def finish(self, job_id: str, result: str | None, error: str | None) -> bool: ...
    def interrupt_expired(self, now: float) -> int: ...
    def add_schedule(self, schedule: Schedule) -> None: ...
    def list_schedules(self, agent_id: str) -> list[Schedule]: ...
    def disable_schedule(self, agent_id: str, schedule_id: str) -> bool: ...
    def materialize_due(self, now: float) -> int: ...

class Runtime:
    def __init__(self, agents: AgentRepository, repository: RuntimeRepository, provider: Provider):
        self.agents, self.repository, self.provider = agents, repository, provider

    def enqueue(self, agent_id: str, prompt: str, due_at: float) -> Job:
        if self.agents.get_agent(agent_id) is None:
            raise LookupError(agent_id)
        job = Job(str(uuid4()), agent_id, prompt, "queued", due_at)
        self.repository.enqueue(job)
        return job

    def schedule(self, agent_id: str, prompt: str, interval_seconds: int, now: float) -> Schedule:
        if self.agents.get_agent(agent_id) is None:
            raise LookupError(agent_id)
        if not 60 <= interval_seconds <= 2592000:
            raise ValueError("Interval must be between one minute and 30 days")
        schedule = Schedule(str(uuid4()), agent_id, prompt, interval_seconds, now + interval_seconds)
        self.repository.add_schedule(schedule)
        return schedule

    def tick(self, now: float, lease_seconds: float) -> bool:
        self.repository.interrupt_expired(now)
        self.repository.materialize_due(now)
        job = self.repository.claim(now, now + lease_seconds)
        if job is None:
            return False
        try:
            agent = self.agents.get_agent(job.agent_id)
            if agent is None:
                raise LookupError(job.agent_id)
            result = self.provider.execute(agent, job.prompt)
        except Exception:
            self.repository.finish(job.id, None, "Provider execution failed")
        else:
            self.repository.finish(job.id, result, None)
        return True
