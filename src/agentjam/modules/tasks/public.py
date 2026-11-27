from dataclasses import dataclass
from typing import Protocol
from agentjam.modules.agents.public import Agent, AgentRepository
from uuid import uuid4

@dataclass(frozen=True)
class Task:
    id: str
    agent_id: str
    prompt: str
    result: str

class ProviderError(RuntimeError):
    pass

class Provider(Protocol):
    def execute(self, agent: Agent, prompt: str) -> str: ...

class TaskRepository(Protocol):
    def save_task(self, task: Task) -> None: ...
    def list_tasks(self, agent_id: str) -> list[Task]: ...

class TaskService:
    def __init__(self, agents: AgentRepository, tasks: TaskRepository, provider: Provider):
        self.agents, self.tasks, self.provider = agents, tasks, provider

    def run(self, agent_id: str, prompt: str) -> Task:
        agent = self.agents.get_agent(agent_id)
        if agent is None:
            raise LookupError(agent_id)
        task = Task(str(uuid4()), agent_id, prompt, self.provider.execute(agent, prompt))
        self.tasks.save_task(task)
        return task
