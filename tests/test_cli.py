"""Tests for CLI utility output contracts."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from acbench.orchestrator.cli import run_doctor


class CLITests(unittest.TestCase):
    def test_run_doctor_reports_standalone_backend(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_doctor()

        payload = json.loads(stream.getvalue())
        self.assertEqual(result, 0)
        self.assertIn("acbench_code", payload)
        self.assertEqual(
            payload["acbench_code"]["extra_checks"]["backend_type"],
            "standalone-local-code",
        )


if __name__ == "__main__":
    unittest.main()
