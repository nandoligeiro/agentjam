from agentjam.adapters.sqlite import SQLiteStore
from agentjam.modules.context.public import Memory

class SQLiteContextStore:
    def __init__(self, store: SQLiteStore):
        self.store = store
        with store.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS agent_skills (
                    agent_id TEXT NOT NULL REFERENCES agents(id),
                    skill_id TEXT NOT NULL, position INTEGER NOT NULL,
                    PRIMARY KEY(agent_id,skill_id)
                );
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id TEXT PRIMARY KEY, agent_id TEXT NOT NULL REFERENCES agents(id),
                    text TEXT NOT NULL, created_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS memory_agent_time ON agent_memory(agent_id,created_at);
            """)

    def selected_skills(self, agent_id):
        with self.store.connection() as db:
            return [row[0] for row in db.execute(
                "SELECT skill_id FROM agent_skills WHERE agent_id=? ORDER BY position",(agent_id,))]

    def set_skills(self, agent_id, skill_ids):
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM agent_skills WHERE agent_id=?",(agent_id,))
            db.executemany("INSERT INTO agent_skills VALUES(?,?,?)",
                           [(agent_id,sid,i) for i,sid in enumerate(skill_ids)])

    def list_memory(self, agent_id):
        with self.store.connection() as db:
            return [Memory(*row) for row in db.execute(
                "SELECT id,agent_id,text,created_at FROM agent_memory WHERE agent_id=? ORDER BY created_at DESC,rowid DESC",(agent_id,))]

    def add_memory(self, memory):
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT count(*) FROM agent_memory WHERE agent_id=?",(memory.agent_id,)).fetchone()[0]>=100:
                raise ValueError("Memory limit reached; delete an entry first")
            db.execute("INSERT INTO agent_memory VALUES(?,?,?,?)",
                       (memory.id,memory.agent_id,memory.text,memory.created_at))

    def delete_memory(self, agent_id,memory_id):
        with self.store.connection() as db:
            return bool(db.execute("DELETE FROM agent_memory WHERE agent_id=? AND id=?",(agent_id,memory_id)).rowcount)
