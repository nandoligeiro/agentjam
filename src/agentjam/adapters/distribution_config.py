"""Load explicitly trusted local YAML manifests; never from HTTP requests."""
import os
from pathlib import Path
import yaml
from agentjam.modules.distribution.public import Distribution, community_distribution

MAX_MANIFEST_BYTES = 65536

def configured_distribution() -> Distribution:
    path = os.getenv("AGENTJAM_DISTRIBUTION")
    if not path:
        return community_distribution()
    manifest = Path(path).expanduser().resolve(strict=True)
    with manifest.open("rb") as stream:
        data = stream.read(MAX_MANIFEST_BYTES+1)
    if len(data)>MAX_MANIFEST_BYTES:
        raise ValueError("Distribution manifest too large")
    distribution = Distribution.model_validate(yaml.safe_load(data))
    roots = []
    for value in distribution.spec.skills.sources:
        root = Path(value).expanduser()
        roots.append(str((manifest.parent/root).resolve() if not root.is_absolute() else root.resolve()))
    distribution.spec.skills.sources = roots
    return distribution
