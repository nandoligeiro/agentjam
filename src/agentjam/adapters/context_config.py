import os
from pathlib import Path
from agentjam.adapters.context_sqlite import SQLiteContextStore
from agentjam.adapters.skills_filesystem import FilesystemSkillsProvider
from agentjam.modules.context.public import ContextService, ContextualProvider

def configured_context(store, provider, distribution=None):
    configured = os.getenv("AGENTJAM_SKILLS_PATHS")
    values = configured.split(os.pathsep) if configured is not None else (distribution.spec.skills.sources if distribution else [])
    roots = tuple(Path(p) for p in values if p)
    context = ContextService(SQLiteContextStore(store), FilesystemSkillsProvider(roots))
    return context, ContextualProvider(provider, context)
