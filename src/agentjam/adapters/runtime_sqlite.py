from uuid import uuid4
from agentjam.adapters.sqlite import SQLiteStore
from agentjam.modules.runtime.public import Job, Schedule

_JOB_FIELDS = "id,agent_id,prompt,status,due_at,result,error"
_SCHEDULE_FIELDS = "id,agent_id,prompt,interval_seconds,next_at,enabled"

class SQLiteRuntimeStore:
    def __init__(self, store: SQLiteStore):
        self.store = store
        with store.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runtime_jobs (
                    id TEXT PRIMARY KEY, agent_id TEXT NOT NULL REFERENCES agents(id),
                    prompt TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN
                    ('queued','running','succeeded','failed','interrupted')),
                    due_at REAL NOT NULL, result TEXT, error TEXT, deadline REAL,
                    schedule_id TEXT
                );
                CREATE INDEX IF NOT EXISTS runtime_jobs_due ON runtime_jobs(status,due_at);
                CREATE TABLE IF NOT EXISTS runtime_schedules (
                    id TEXT PRIMARY KEY, agent_id TEXT NOT NULL REFERENCES agents(id),
                    prompt TEXT NOT NULL, interval_seconds INTEGER NOT NULL,
                    next_at REAL NOT NULL, enabled INTEGER NOT NULL DEFAULT 1
                );
            """)

    def enqueue(self, job):
        with self.store.connection() as db:
            db.execute("INSERT INTO runtime_jobs(id,agent_id,prompt,status,due_at) VALUES(?,?,?,?,?)",
                       (job.id, job.agent_id, job.prompt, job.status, job.due_at))

    def list_jobs(self, agent_id):
        with self.store.connection() as db:
            return [Job(*row) for row in db.execute(
                f"SELECT {_JOB_FIELDS} FROM runtime_jobs WHERE agent_id=? ORDER BY rowid", (agent_id,))]

    def claim(self, now, deadline):
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM runtime_jobs WHERE status='running' LIMIT 1").fetchone():
                return None
            row = db.execute(f"SELECT {_JOB_FIELDS} FROM runtime_jobs WHERE status='queued' AND due_at<=? ORDER BY due_at,rowid LIMIT 1", (now,)).fetchone()
            if not row:
                return None
            db.execute("UPDATE runtime_jobs SET status='running',deadline=? WHERE id=?", (deadline,row[0]))
            return Job(row[0],row[1],row[2],"running",row[4])

    def finish(self, job_id, result, error):
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            status = "failed" if error is not None else "succeeded"
            changed = db.execute("UPDATE runtime_jobs SET status=?,result=?,error=?,deadline=NULL WHERE id=? AND status='running'",
                                 (status,result,error,job_id)).rowcount
            if changed and status == "succeeded":
                db.execute("INSERT INTO tasks(id,agent_id,prompt,result) SELECT id,agent_id,prompt,result FROM runtime_jobs WHERE id=?", (job_id,))
            return bool(changed)

    def interrupt_expired(self, now):
        with self.store.connection() as db:
            return db.execute("UPDATE runtime_jobs SET status='interrupted',error='Execution outcome unknown; review before resubmitting',deadline=NULL WHERE status='running' AND deadline<=?", (now,)).rowcount

    def add_schedule(self, schedule):
        with self.store.connection() as db:
            db.execute("INSERT INTO runtime_schedules VALUES(?,?,?,?,?,?)",
                       (schedule.id,schedule.agent_id,schedule.prompt,schedule.interval_seconds,schedule.next_at,int(schedule.enabled)))

    def list_schedules(self, agent_id):
        with self.store.connection() as db:
            return [Schedule(*row[:5],bool(row[5])) for row in db.execute(
                f"SELECT {_SCHEDULE_FIELDS} FROM runtime_schedules WHERE agent_id=? ORDER BY rowid", (agent_id,))]

    def disable_schedule(self, agent_id, schedule_id):
        with self.store.connection() as db:
            return bool(db.execute("UPDATE runtime_schedules SET enabled=0 WHERE agent_id=? AND id=?", (agent_id,schedule_id)).rowcount)

    def materialize_due(self, now):
        count = 0
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT id,agent_id,prompt,interval_seconds,next_at FROM runtime_schedules WHERE enabled=1 AND next_at<=?", (now,)).fetchall()
            for sid, aid, prompt, interval, due in rows:
                if not db.execute("SELECT 1 FROM runtime_jobs WHERE schedule_id=? AND status IN ('queued','running')", (sid,)).fetchone():
                    db.execute("INSERT INTO runtime_jobs(id,agent_id,prompt,status,due_at,schedule_id) VALUES(?,?,?,'queued',?,?)", (str(uuid4()),aid,prompt,now,sid))
                    count += 1
                next_at = due + (int((now-due)//interval)+1)*interval
                db.execute("UPDATE runtime_schedules SET next_at=? WHERE id=?", (next_at,sid))
        return count
