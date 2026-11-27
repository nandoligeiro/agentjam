from agentjam.adapters.sqlite import SQLiteStore
from agentjam.modules.tools.public import Observation

class SQLiteObservationStore:
    def __init__(self, store: SQLiteStore):
        self.store = store
        with store.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tool_observations (
                id TEXT PRIMARY KEY, tool_id TEXT NOT NULL, observed_at REAL NOT NULL,
                status TEXT NOT NULL, alarm_count INTEGER, error TEXT
            )""")
    def save(self, observation):
        with self.store.connection() as db:
            db.execute("INSERT INTO tool_observations VALUES(?,?,?,?,?,?)",
                       (observation.id,observation.tool_id,observation.observed_at,
                        observation.status,observation.alarm_count,observation.error))
            # Retain at most 1000 observations per tool.
            db.execute("""DELETE FROM tool_observations WHERE tool_id=? AND id NOT IN
                        (SELECT id FROM tool_observations WHERE tool_id=? ORDER BY rowid DESC LIMIT 1000)""",
                       (observation.tool_id,observation.tool_id))
    def recent(self, limit=100):
        with self.store.connection() as db:
            return [Observation(*row) for row in db.execute(
                "SELECT id,tool_id,observed_at,status,alarm_count,error FROM tool_observations ORDER BY rowid DESC LIMIT ?",
                (max(1,min(limit,100)),))]
