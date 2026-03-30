"""Tests for the standalone-first repository layout."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

from acbench.models.scenario import ScenarioSpec


class StandaloneLayoutTests(unittest.TestCase):
    def test_canonical_standalone_scenarios_load(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative_path in (
            "standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json",
            "standalone/scenarios/code/samplepkg__smoke_local.scenario.json",
            "standalone/scenarios/code/astronomy_shop__product_catalog_seed_defect.scenario.json",
            "standalone/scenarios/combined/samplepkg__local_fixture.scenario.json",
        ):
            scenario = ScenarioSpec.from_file(root / relative_path)
            self.assertTrue(scenario.scenario_id)

    def test_new_namespace_packages_are_importable(self) -> None:
        for module_name in (
            "acbench.standalone.benchmarks.code",
            "acbench.standalone.benchmarks.ops",
            "acbench.standalone.benchmarks.combined",
            "acbench.standalone.runtimes.code",
            "acbench.standalone.runtimes.ops",
            "acbench.standalone.runtimes.combined",
        ):
            module = importlib.import_module(module_name)
            self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
