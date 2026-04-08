"""Tests for the standalone-first repository layout."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

from acbench.models.scenario import ScenarioSpec


class StandaloneLayoutTests(unittest.TestCase):
    def test_canonical_task_scenarios_load(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative_path in (
            "tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json",
            "tasks/scenarios/code/samplepkg__smoke_local.scenario.json",
            "tasks/scenarios/code/astronomy_shop__product_catalog_seed_defect.scenario.json",
            "tasks/scenarios/combined/samplepkg__local_fixture.scenario.json",
        ):
            scenario = ScenarioSpec.from_file(root / relative_path)
            self.assertTrue(scenario.scenario_id)

    def test_new_namespace_packages_are_importable(self) -> None:
        for module_name in (
            "acbench.orchestrator",
            "acbench.tasks",
            "acbench.services",
            "acbench.evaluation",
            "acbench.executors.backends.code",
            "acbench.executors.backends.ops",
        ):
            module = importlib.import_module(module_name)
            self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
