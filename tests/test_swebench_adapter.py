"""Tests for SWE-bench-Live adapter helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from acbench.adapters.swebench import SWEBenchCodeExecutor
from acbench.backends.code.native_upstream import inspect_native_environment
from acbench.models.runtime import RunConfig
from acbench.models.scenario import ScenarioSpec


class FakeNativePatchAgent:
    """Return a simple synthetic patch for native SWE-bench tests."""

    def generate_patch(self, scenario, run_config, *, output_dir):
        patch_text = "diff --git a/sample.txt b/sample.txt\n--- a/sample.txt\n+++ b/sample.txt\n@@ -1 +1 @@\n-old\n+new\n"
        generated_patch_path = output_dir / "fake_native_agent_patch.diff"
        generated_patch_path.write_text(patch_text, encoding="utf-8")
        return {
            "patch_text": patch_text,
            "generated_patch_path": str(generated_patch_path),
        }


class SWEBenchAdapterTests(unittest.TestCase):
    def _build_native_scenario(self, instance_path: Path) -> ScenarioSpec:
        return ScenarioSpec.from_dict(
            {
                "scenario_id": "native-swebench",
                "title": "native",
                "mode": "code_only",
                "service": {
                    "application": "app",
                    "service": "svc",
                },
                "code_fault": {
                    "source": "swe-bench-live",
                    "defect_id": "d1",
                    "instance_path": str(instance_path),
                    "platform": "linux",
                },
            }
        )

    def test_native_upstream_environment_detects_repo_layout(self) -> None:
        preflight = inspect_native_environment()
        self.assertTrue(preflight.repo_root.endswith("SWE-bench-Live"))
        self.assertTrue(preflight.launch_root.endswith("SWE-bench-Live\\launch"))
        self.assertEqual(preflight.backend_type, "upstream-native")

    def test_preflight_detects_repo_layout(self) -> None:
        preflight = SWEBenchCodeExecutor.preflight()
        self.assertTrue(preflight.repo_root.endswith("SWE-bench-Live"))
        self.assertTrue(preflight.launch_root.endswith("SWE-bench-Live\\launch"))
        self.assertEqual(preflight.backend_type, "upstream-native")

    def test_standalone_preflight_uses_internal_backend_type(self) -> None:
        preflight = SWEBenchCodeExecutor.standalone_preflight()
        self.assertEqual(preflight.backend_type, "standalone-local-code")
        self.assertTrue(preflight.import_ready)

    def test_preflight_for_repo_backed_scenario_uses_standalone_path(self) -> None:
        scenario = ScenarioSpec.from_dict(
            {
                "scenario_id": "repo-backed-swe-style",
                "title": "repo backed",
                "mode": "code_only",
                "service": {
                    "application": "app",
                    "service": "svc",
                    "repository_path": str(Path.cwd()),
                },
                "code_fault": {
                    "source": "swe-bench-live",
                    "defect_id": "d1",
                },
                "build": {
                    "test_cmds": ["echo ok"],
                },
            }
        )

        preflight = SWEBenchCodeExecutor.preflight_for_scenario(scenario)

        self.assertEqual(preflight.backend_type, "standalone-local-code")

    def test_preflight_for_native_instance_uses_upstream_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"p","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"],"docker_image":"example/native:latest"}',
                encoding="utf-8",
            )
            scenario = self._build_native_scenario(instance_path)

            preflight = SWEBenchCodeExecutor.preflight_for_scenario(scenario)

            self.assertEqual(preflight.backend_type, "upstream-native")

    def test_build_instance_payload_uses_gold_patch_only_when_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"gold-patch","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"]}',
                encoding="utf-8",
            )

            instance = SWEBenchCodeExecutor.build_instance_payload(
                self._build_native_scenario(instance_path),
                RunConfig(code_patch_path="gold"),
            )

            self.assertEqual(instance["pred_patch"], "gold-patch")

    def test_build_instance_payload_accepts_agent_ref_without_pred_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"gold-patch","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"]}',
                encoding="utf-8",
            )

            instance = SWEBenchCodeExecutor.build_instance_payload(
                self._build_native_scenario(instance_path),
                RunConfig(code_agent_ref="pkg.module:Agent"),
            )

            self.assertEqual(instance["pred_patch"], "")

    def test_build_instance_payload_uses_agent_generated_patch_when_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"gold-patch","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"]}',
                encoding="utf-8",
            )
            patch_text = "diff --git a/a b/a\n--- a/a\n+++ b/a\n@@ -1 +1 @@\n-old\n+new\n"

            instance = SWEBenchCodeExecutor.build_instance_payload(
                self._build_native_scenario(instance_path),
                RunConfig(code_agent_ref="tests.test_swebench_adapter:FakeNativePatchAgent"),
                patch_override=patch_text,
            )

            self.assertEqual(instance["pred_patch"], patch_text)

    def test_build_instance_payload_rejects_implicit_gold_patch_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"gold-patch","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "requires one of"):
                SWEBenchCodeExecutor.build_instance_payload(
                    self._build_native_scenario(instance_path),
                    RunConfig(),
                )

    def test_resolve_agent_patch_invokes_generate_patch_for_native_swebench(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                '{"instance_id":"native-1","repo":"owner/repo","patch":"gold-patch","test_patch":"t","PASS_TO_PASS":[],"FAIL_TO_PASS":[],"test_cmds":["pytest"]}',
                encoding="utf-8",
            )

            artifacts = SWEBenchCodeExecutor._resolve_agent_patch(
                self._build_native_scenario(instance_path),
                RunConfig(code_agent_ref="tests.test_swebench_adapter:FakeNativePatchAgent"),
                Path(tmp_dir),
            )

            self.assertIn("patch_text", artifacts)
            self.assertTrue(Path(artifacts["generated_patch_path"]).exists())

    def test_execute_rejects_non_native_scenario(self) -> None:
        scenario = ScenarioSpec.from_dict(
            {
                "scenario_id": "repo-backed-swe-style",
                "title": "repo backed",
                "mode": "code_only",
                "service": {
                    "application": "app",
                    "service": "svc",
                    "repository_path": str(Path.cwd()),
                },
                "code_fault": {
                    "source": "swe-bench-live",
                    "defect_id": "d1",
                },
                "build": {
                    "test_cmds": ["echo ok"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError):
                SWEBenchCodeExecutor().execute(
                    scenario,
                    Path(tmp_dir),
                    RunConfig(dry_run=False),
                )


if __name__ == "__main__":
    unittest.main()
