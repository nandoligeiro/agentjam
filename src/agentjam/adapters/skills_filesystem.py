"""Read-only discovery of explicitly configured local SKILL.md files."""
from pathlib import Path
import hashlib
from agentjam.modules.context.public import Skill

MAX_SKILL_BYTES = 32000

class FilesystemSkillsProvider:
    def __init__(self, roots: tuple[Path, ...]):
        self.roots = tuple(p.resolve(strict=True) for p in roots)
        if any(not p.is_dir() for p in self.roots):
            raise ValueError("Skill source must be a directory")

    def _entries(self):
        entries = {}
        for index, root in enumerate(self.roots):
            # Do not follow symlinks; reject paths resolved outside configured roots.
            for file in sorted(root.rglob("SKILL.md")):
                relative = file.relative_to(root)
                if any(part.startswith(".") for part in relative.parts):
                    continue
                if any((root.joinpath(*relative.parts[:i])).is_symlink()
                       for i in range(1, len(relative.parts)+1)):
                    continue
                try:
                    resolved = file.resolve(strict=True)
                    if not resolved.is_relative_to(root) or not resolved.is_file() or resolved.stat().st_size > MAX_SKILL_BYTES:
                        continue
                except OSError:
                    continue
                key = hashlib.sha256(f"{index}:{relative.as_posix()}".encode()).hexdigest()[:24]
                name = relative.parent.as_posix() if relative.parent != Path(".") else root.name
                entries[key] = (Skill(key, name, f"source-{index+1}"), root, relative)
                if len(entries) >= 500:
                    return entries
        return entries

    def list_skills(self):
        return [entry[0] for entry in self._entries().values()]

    def read_skill(self, skill_id):
        entry = self._entries().get(skill_id)
        if entry is None:
            raise LookupError(skill_id)
        _, root, relative = entry
        file = root / relative
        if any((root.joinpath(*relative.parts[:i])).is_symlink()
               for i in range(1,len(relative.parts)+1)):
            raise ValueError("Symlink not allowed")
        if not file.resolve(strict=True).is_relative_to(root):
            raise ValueError("Skill outside source")
        with file.open("rb") as stream:
            data = stream.read(MAX_SKILL_BYTES+1)
        if len(data) > MAX_SKILL_BYTES:
            raise ValueError("Skill too large")
        return data.decode("utf-8")
