import sqlite3
from contextlib import contextmanager
from agentjam.modules.agents.public import Agent
from agentjam.modules.tasks.public import Task

class SQLiteStore:
    def __init__(self, path: str):
        self.path = path
        with self.connection() as db:
            db.executescript("CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY,name TEXT NOT NULL,instructions TEXT NOT NULL); CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,agent_id TEXT NOT NULL REFERENCES agents(id),prompt TEXT NOT NULL,result TEXT NOT NULL);")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            with db:
                yield db
        finally:
            db.close()

    def save_agent(self, agent):
        with self.connection() as db:
            db.execute("INSERT INTO agents VALUES(?,?,?)", (agent.id,agent.name,agent.instructions))

    def get_agent(self, agent_id):
        with self.connection() as db:
            row = db.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
            return Agent(*row) if row else None

    def list_agents(self):
        with self.connection() as db:
            return [Agent(*row) for row in db.execute("SELECT * FROM agents ORDER BY rowid")]

    def save_task(self, task):
        with self.connection() as db:
            db.execute("INSERT INTO tasks VALUES(?,?,?,?)", (task.id,task.agent_id,task.prompt,task.result))

    def list_tasks(self, agent_id):
        with self.connection() as db:
            return [Task(*row) for row in db.execute("SELECT * FROM tasks WHERE agent_id=? ORDER BY rowid", (agent_id,))]
