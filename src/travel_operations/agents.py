"""Stateless Bedrock agent specifications and Lambda-backed tool contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSpec:
    name: str
    instruction_path: str
    tool_name: str


AGENTS = (
    AgentSpec("travel-coordinator", "prompts/agents/travel-coordinator/v1.md", "coordinate_travel"),
    AgentSpec("policy", "prompts/agents/policy/v1.md", "lookup_policy"),
    AgentSpec("visa", "prompts/agents/visa/v1.md", "check_visa"),
    AgentSpec("insurance", "prompts/agents/insurance/v1.md", "calculate_insurance"),
    AgentSpec("risk", "prompts/agents/risk/v1.md", "assess_risk"),
    AgentSpec("approval", "prompts/agents/approval/v1.md", "prepare_approval"),
)
