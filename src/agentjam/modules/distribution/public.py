"""Versioned distribution contract; configuration is not an authorization boundary."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Metadata(StrictModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")

class Branding(StrictModel):
    name: str = Field(min_length=1,max_length=80)
    tagline: str = Field(default="Open Agent Workspace",max_length=120)
    initials: str = Field(default="AJ",min_length=1,max_length=4)
    primaryColor: str = Field(default="#5eead4",pattern=r"^#[0-9a-fA-F]{6}$")

class ProviderDefaults(StrictModel):
    type: Literal["mock","acp"] = "mock"

class SkillDefaults(StrictModel):
    sources: list[str] = Field(default_factory=list,max_length=16)

class DistributionSpec(StrictModel):
    branding: Branding
    provider: ProviderDefaults = Field(default_factory=ProviderDefaults)
    skills: SkillDefaults = Field(default_factory=SkillDefaults)

class Distribution(StrictModel):
    apiVersion: Literal["agentjam/v1alpha1"]
    kind: Literal["Distribution"]
    metadata: Metadata
    spec: DistributionSpec

def community_distribution() -> Distribution:
    return Distribution(apiVersion="agentjam/v1alpha1",kind="Distribution",
                        metadata=Metadata(name="community"),
                        spec=DistributionSpec(branding=Branding(name="AgentJam")))

def public_metadata(distribution: Distribution) -> dict:
    return {"name":distribution.metadata.name,"branding":distribution.spec.branding.model_dump()}
