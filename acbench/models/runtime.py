"""Runtime configuration models for the ACBench prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RunConfig:
    """Top-level run configuration passed into executors."""

    dry_run: bool = False
    max_steps: int = 10
    keep_artifacts: bool = True
    aiops_agent_type: str = "unconfigured"
    code_agent_type: str = "unconfigured"
    aiops_agent_ref: str = ""
    code_agent_ref: str = ""
    agent_config_path: str = ""
    agent_profile_name: str = ""
    code_agent_config: dict[str, Any] = field(default_factory=dict)
    ops_agent_config: dict[str, Any] = field(default_factory=dict)
    code_patch_path: str = ""
    openai_model: str = ""
    openai_api_key_env: str = "OPENAI_API_KEY"
    openai_base_url: str = ""
    anthropic_model: str = ""
    anthropic_api_key_env: str = "ANTHROPIC_API_KEY"
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_version: str = "2023-06-01"
