from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Agent:
    id: str
    name: str
    instructions: str

class AgentRepository(Protocol):
    def save_agent(self, agent: Agent) -> None: ...
    def get_agent(self, agent_id: str) -> Agent | None: ...
    def list_agents(self) -> list[Agent]: ...
