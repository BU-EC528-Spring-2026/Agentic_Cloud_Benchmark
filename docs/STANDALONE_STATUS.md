# Standalone Status

This document describes what works when only this repository is present.

## Works With This Repository Alone

- local code benchmark execution
- OpenAI-backed local code repair prototype
- local demo suite
- scenario validation
- report generation
- batch evaluation utilities

## Does Not Require Upstream Repositories

Standalone local mode does not require:

- `AIOpsLab`
- `SWE-bench-Live`

## Still Requires Upstream Repositories

These paths are optional integrations and still require sibling checkouts:

- live `AIOpsLab` ops scenarios
- native `SWE-bench-Live` scenarios

## Intended Usage

If you are cloning the repository for the first time, the standalone local code path should be your first run target.

Use the live bridge paths only after the standalone setup succeeds.
