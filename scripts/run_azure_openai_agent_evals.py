#!/usr/bin/env python3
"""Run configured ACBench manifests with an Azure OpenAI agent profile."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from acbench.evaluation.evaluate import evaluate_predictions
from acbench.orchestrator.runner import ACBenchRunner
from acbench.paths import resolve_repo_path


def _load_config(config_path: str | Path) -> dict:
    path = resolve_repo_path(config_path)
    return json.loads(path.read_text(encoding="utf-8"))


def _apply_azure_credentials(config: dict) -> str:
    azure = config.get("azure_openai", {})
    env_name = str(azure.get("api_key_env", "AZURE_OPENAI_API_KEY"))
    api_key = str(azure.get("api_key", ""))
    if api_key:
        os.environ[env_name] = api_key
    if not os.environ.get(env_name, ""):
        raise ValueError(
            f"No API key available. Set `{env_name}` in the environment or fill `azure_openai.api_key` in the config."
        )
    return env_name


def _materialize_predictions(
    manifest_path: Path,
    *,
    agent_config: str,
    max_steps: int,
    keep_artifacts: bool,
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runner = ACBenchRunner()
    predictions: dict[str, dict] = {
        "_defaults": {
            "agent_config": agent_config,
            "max_steps": max_steps,
            "keep_artifacts": keep_artifacts,
        }
    }
    for entry in manifest["scenarios"]:
        scenario = runner.load_scenario(entry["scenario"])
        predictions[scenario.scenario_id] = {}
    return predictions


def run_from_config(config_path: str | Path) -> dict:
    config = _load_config(config_path)
    _apply_azure_credentials(config)
    agent = config.get("agent", {})

    default_agent_config = str(
        agent.get("agent_config", "configs/agents/azure_openai.example.json")
    )
    defaults = {
        "agent_config": str(resolve_repo_path(default_agent_config)),
        "max_steps": int(agent.get("max_steps", 25)),
        "keep_artifacts": bool(agent.get("keep_artifacts", True)),
    }

    summary_output = resolve_repo_path(
        config.get("summary_output", "runs/azure_openai_agent_batch_summary.json")
    )
    bundle: dict[str, dict] = {"runs": {}}

    with tempfile.TemporaryDirectory(prefix="acbench-azure-openai-agent-") as temp_dir:
        temp_root = Path(temp_dir)
        for run in config.get("runs", []):
            name = str(run.get("name", "unnamed"))
            manifest_path = resolve_repo_path(run["manifest"])
            output_path = resolve_repo_path(run["output"])
            predictions = _materialize_predictions(
                manifest_path,
                agent_config=defaults["agent_config"],
                max_steps=defaults["max_steps"],
                keep_artifacts=defaults["keep_artifacts"],
            )
            predictions_path = temp_root / f"{name}_predictions.json"
            predictions_path.write_text(
                json.dumps(predictions, indent=2),
                encoding="utf-8",
            )
            bundle["runs"][name] = evaluate_predictions(
                manifest_path=manifest_path,
                predictions_path=predictions_path,
                output_path=output_path,
            )

    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ACBench manifests with Azure OpenAI-backed agent profiles."
    )
    parser.add_argument(
        "--config",
        default="configs/azure_openai_direct.local.json",
        help="Path to the local Azure OpenAI batch config JSON.",
    )
    args = parser.parse_args()
    bundle = run_from_config(args.config)
    print(json.dumps(bundle, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
