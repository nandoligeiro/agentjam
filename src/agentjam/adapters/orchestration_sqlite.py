from agentjam.adapters.sqlite import SQLiteStore
from agentjam.modules.orchestration.public import Delegation, MAX_DEPTH, MAX_CHILDREN, MAX_DESCENDANTS

class SQLiteDelegationStore:
    def __init__(self, store: SQLiteStore):
        self.store = store
        with store.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS job_delegations (
                    job_id TEXT PRIMARY KEY REFERENCES runtime_jobs(id),
                    parent_job_id TEXT NOT NULL REFERENCES runtime_jobs(id),
                    root_job_id TEXT NOT NULL REFERENCES runtime_jobs(id),
                    source_agent_id TEXT NOT NULL REFERENCES agents(id),
                    target_agent_id TEXT NOT NULL REFERENCES agents(id),
                    depth INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS delegation_parent ON job_delegations(parent_job_id);
                CREATE INDEX IF NOT EXISTS delegation_root ON job_delegations(root_job_id);
            """)

    def delegate(self, parent_id, source_id, job):
        with self.store.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            parent = db.execute("SELECT agent_id,status FROM runtime_jobs WHERE id=?", (parent_id,)).fetchone()
            if parent is None or parent[0] != source_id:
                raise LookupError("Parent job not found for source agent")
            if parent[1] != "succeeded":
                raise ValueError("Only completed successful jobs can be delegated")
            ancestors = {source_id}
            cursor, depth, root = parent_id, 1, parent_id
            while True:
                link = db.execute("SELECT parent_job_id,source_agent_id FROM job_delegations WHERE job_id=?", (cursor,)).fetchone()
                if not link:
                    break
                cursor, ancestor = link
                ancestors.add(ancestor)
                root = cursor
                depth += 1
                if depth > MAX_DEPTH:
                    raise ValueError("Delegation depth limit reached")
            if job.agent_id in ancestors:
                raise ValueError("Delegation would repeat an ancestor agent")
            if db.execute("SELECT count(*) FROM job_delegations WHERE parent_job_id=?", (parent_id,)).fetchone()[0] >= MAX_CHILDREN:
                raise ValueError("Parent delegation limit reached")
            if db.execute("SELECT count(*) FROM job_delegations WHERE root_job_id=?", (root,)).fetchone()[0] >= MAX_DESCENDANTS:
                raise ValueError("Workflow delegation limit reached")
            db.execute("INSERT INTO runtime_jobs(id,agent_id,prompt,status,due_at) VALUES(?,?,?,?,?)",
                       (job.id,job.agent_id,job.prompt,job.status,job.due_at))
            db.execute("INSERT INTO job_delegations VALUES(?,?,?,?,?,?)",
                       (job.id,parent_id,root,source_id,job.agent_id,depth))
            return Delegation(job.id,parent_id,source_id,job.agent_id,depth)

    def list_delegations(self, agent_id):
        with self.store.connection() as db:
            return [Delegation(*row) for row in db.execute(
                "SELECT job_id,parent_job_id,source_agent_id,target_agent_id,depth FROM job_delegations WHERE source_agent_id=? OR target_agent_id=? ORDER BY rowid",
                (agent_id,agent_id))]
