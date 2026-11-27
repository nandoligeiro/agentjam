import os
from pathlib import Path
from agentjam.adapters.context_sqlite import SQLiteContextStore
from agentjam.adapters.skills_filesystem import FilesystemSkillsProvider
from agentjam.modules.context.public import ContextService, ContextualProvider

def configured_context(store, provider):
    roots = tuple(Path(p) for p in os.getenv("AGENTJAM_SKILLS_PATHS","").split(os.pathsep) if p)
    context = ContextService(SQLiteContextStore(store), FilesystemSkillsProvider(roots))
    return context, ContextualProvider(provider, context)
