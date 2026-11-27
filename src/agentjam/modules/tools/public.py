"""Deterministic tools run without an agent provider or model invocation."""
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4
import time

@dataclass(frozen=True)
class Observation:
    id: str
    tool_id: str
    observed_at: float
    status: str
    alarm_count: int | None
    error: str | None = None

class Tool(Protocol):
    id: str
    def collect(self) -> int: ...

class ObservationRepository(Protocol):
    def save(self, observation: Observation) -> None: ...
    def recent(self, limit: int) -> list[Observation]: ...

class ToolFailure(Exception):
    """A controlled error without subprocess output or credentials."""

class Registry:
    def __init__(self, tools: list[Tool], repository: ObservationRepository):
        self.tools = {tool.id: tool for tool in tools}
        self.repository = repository

    def ids(self) -> list[str]:
        return sorted(self.tools)

    def run(self, tool_id: str) -> Observation:
        if tool_id not in self.tools:
            raise LookupError("Unknown or disabled tool")
        try:
            count = self.tools[tool_id].collect()
            if type(count) is not int or count < 0:
                raise ToolFailure("invalid_result")
            observation = Observation(str(uuid4()), tool_id, time.time(),
                                      "attention" if count else "clear", count)
        except ToolFailure as exc:
            observation = Observation(str(uuid4()), tool_id, time.time(),
                                      "error", None, str(exc))
        self.repository.save(observation)
        return observation
