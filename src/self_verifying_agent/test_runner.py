from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

from .state import AgentState


def run_tests(state: AgentState) -> AgentState:
    """Run pytest in a temporary directory against the current code and tests.

    Writes `impl.py` for the implementation and `test_impl.py` for the tests,
    then executes pytest as a subprocess, capturing stdout/stderr and exit code.
    """

    print(">>> Agent is running tests...")
    if state.code is None or state.tests is None:
        state.test_results = {
            "status": "error",
            "reason": "Missing code or tests before running test_runner.",
        }
        return state

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        impl_path = tmpdir / "impl.py"
        test_path = tmpdir / "test_impl.py"

        impl_path.write_text(state.code, encoding="utf-8")
        test_path.write_text(state.tests, encoding="utf-8")

        # Run pytest
        cmd = [sys.executable, "-m", "pytest", str(test_path)]
        proc = subprocess.run(
            cmd,
            cwd=str(tmpdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        result: Dict[str, Any] = {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

        state.test_results = result
        return state
