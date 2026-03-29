"""Tests for the internal ACBench code runtime engine layer."""

from __future__ import annotations

from pathlib import Path
import unittest
from unittest import mock

from acbench.backends.code.engine import (
    StandaloneLocalEngine,
    UpstreamSWEBenchEngine,
    _patch_upstream_setup_runtime,
    build_default_engine,
    build_engine_for_instance,
)
from acbench.backends.code.runtime import CodeRunRequest, NativeCodeInstance


class CodeEngineTests(unittest.TestCase):
    @mock.patch.object(UpstreamSWEBenchEngine, "_run_upstream_instance")
    def test_upstream_engine_converts_report_into_code_outcome(self, mock_run) -> None:
        mock_run.return_value = {
            "instance_id": "native-1",
            "resolved": True,
            "PASS_TO_PASS": {"success": ["t1"], "failure": []},
            "FAIL_TO_PASS": {"success": ["t2"], "failure": []},
            "logs": {"report_path": "report.json"},
        }
        engine = UpstreamSWEBenchEngine(repo_root=Path("C:/repo"))
        outcome = engine.run(
            CodeRunRequest(
                instance=NativeCodeInstance(
                    instance_id="native-1",
                    repo="owner/repo",
                    platform="linux",
                    patch="p",
                    pred_patch="pp",
                    test_patch="tp",
                    pass_to_pass=["t1"],
                    fail_to_pass=["t2"],
                ),
                output_dir=Path("out"),
            )
        )

        self.assertTrue(outcome.resolved)
        self.assertEqual(outcome.pass_to_pass_success, ["t1"])
        self.assertEqual(outcome.fail_to_pass_success, ["t2"])
        self.assertEqual(outcome.logs["report_path"], "report.json")

    def test_build_default_engine_returns_upstream_bridge(self) -> None:
        engine = build_default_engine()
        self.assertIsInstance(engine, UpstreamSWEBenchEngine)

    def test_build_engine_for_instance_uses_standalone_for_local_repo(self) -> None:
        with mock.patch("pathlib.Path.exists", return_value=True):
            engine = build_engine_for_instance(
                NativeCodeInstance(
                    instance_id="local-1",
                    repo="C:/repo",
                    platform="windows",
                    patch="p",
                    pred_patch="pp",
                    test_patch="tp",
                )
            )
        self.assertIsInstance(engine, StandaloneLocalEngine)

    def test_build_engine_for_instance_keeps_upstream_for_native_docker_case(self) -> None:
        engine = build_engine_for_instance(
            NativeCodeInstance(
                instance_id="native-1",
                repo="owner/repo",
                platform="linux",
                patch="p",
                pred_patch="pp",
                test_patch="tp",
                docker_image="example/native:latest",
            )
        )
        self.assertIsInstance(engine, UpstreamSWEBenchEngine)

    def test_patch_upstream_setup_runtime_keeps_linux_container_patch_paths_posix(self) -> None:
        class _Metadata:
            exit_code = 0

        class _Result:
            metadata = _Metadata()
            output = ""

        class FakeSetupRuntime:
            def __init__(self) -> None:
                self.platform = "linux"
                self.mnt_host = str(Path.cwd() / "tmp")
                self.mnt_container = "/testbed/mnt_tmp"
                self.working_dir = "/testbed"
                self.commands: list[str] = []
                self.copied: list[tuple[str, str]] = []

            def send_command(self, command: str):
                self.commands.append(command)
                return _Result()

            def copy_to_container(self, src: str, dest: str) -> None:
                self.copied.append((src, dest))

            def apply_patch(self, patch: str, verbose: bool = False) -> bool:
                raise AssertionError("original apply_patch should be replaced")

        Path("tmp").mkdir(exist_ok=True)
        _patch_upstream_setup_runtime(FakeSetupRuntime)
        runtime = FakeSetupRuntime()

        success = runtime.apply_patch("diff --git a/x b/x\n", verbose=True)

        self.assertTrue(success)
        self.assertEqual(runtime.copied[0][1], "/testbed")
        self.assertIn('git apply --reject  --whitespace=nowarn  "/testbed/', runtime.commands[0])
        self.assertNotIn("\\", runtime.commands[0])

    def test_patch_upstream_setup_runtime_preserves_non_linux_behavior(self) -> None:
        class FakeSetupRuntime:
            def __init__(self) -> None:
                self.platform = "windows"

            def apply_patch(self, patch: str, verbose: bool = False) -> bool:
                return patch == "expected" and verbose

        _patch_upstream_setup_runtime(FakeSetupRuntime)
        runtime = FakeSetupRuntime()

        self.assertTrue(runtime.apply_patch("expected", verbose=True))


if __name__ == "__main__":
    unittest.main()
