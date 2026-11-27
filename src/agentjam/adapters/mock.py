from agentjam.modules.agents.public import Agent

class MockProvider:
    def execute(self, agent: Agent, prompt: str) -> str:
        return f"[MOCK] {agent.name}: {prompt}"
