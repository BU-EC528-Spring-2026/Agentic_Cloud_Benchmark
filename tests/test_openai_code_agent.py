"""Tests for the OpenAI code patch agent helpers."""

from __future__ import annotations

import unittest

from acbench.agents.openai_code import OpenAICodePatchAgent


class OpenAICodePatchAgentTests(unittest.TestCase):
    def test_extract_patch_accepts_fenced_plain_unified_diff(self) -> None:
        response = """
Here is the fix.

```diff
--- a/src/example.py
+++ b/src/example.py
@@ -1,1 +1,1 @@
-return 1
+return 2
```

This should resolve the issue.
"""
        patch = OpenAICodePatchAgent._extract_patch(response)

        self.assertTrue(patch.startswith("--- a/src/example.py"))
        self.assertIn("@@ -1,1 +1,1 @@", patch)

    def test_extract_patch_trims_prose_around_non_fenced_diff(self) -> None:
        response = """
I fixed the bug below.
--- a/src/example.py
+++ b/src/example.py
@@ -1,1 +1,1 @@
-return 1
+return 2
Thanks!
"""
        patch = OpenAICodePatchAgent._extract_patch(response)

        self.assertNotIn("I fixed the bug below.", patch)
        self.assertNotIn("Thanks!", patch)
        self.assertTrue(patch.startswith("--- a/src/example.py"))

    def test_validate_unified_diff_accepts_plain_unified_diff(self) -> None:
        patch = "\n".join(
            [
                "--- a/src/example.py",
                "+++ b/src/example.py",
                "@@ -1,1 +1,1 @@",
                "-return 1",
                "+return 2",
            ]
        )

        self.assertEqual(OpenAICodePatchAgent._validate_unified_diff(patch), "")

    def test_extract_patch_converts_file_block_format(self) -> None:
        response = """
--- FILE: src/example.py ---
@@ -1,1 +1,1 @@
-return 1
+return 2
"""
        patch = OpenAICodePatchAgent._extract_patch(response)

        self.assertTrue(patch.startswith("--- a/src/example.py"))
        self.assertIn("+++ b/src/example.py", patch)

    def test_validate_unified_diff_accepts_semantic_hunk_headers(self) -> None:
        patch = "\n".join(
            [
                "--- a/src/example.py",
                "+++ b/src/example.py",
                "@@ def example(",
                "-return 1",
                "+return 2",
            ]
        )

        self.assertEqual(OpenAICodePatchAgent._validate_unified_diff(patch), "")


if __name__ == "__main__":
    unittest.main()
