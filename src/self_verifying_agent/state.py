from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Shared state for the self-verifying code agent.

    This is the single source of truth passed between LangGraph nodes.
    """

    spec: str = Field(..., description="Original natural-language specification.")
    parsed_spec: Dict[str, Any] = Field(default_factory=dict, description="Structured spec extracted from the natural language description.")

    code: Optional[str] = Field(default=None, description="Current implementation under test.")
    tests: Optional[str] = Field(default=None, description="Pytest test file content for the current spec.")

    test_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw test execution results: exit code, stdout, stderr, parsed failures, etc.",
    )

    error_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured explanation of failures, including type, likely cause, and suggested fix focus.",
    )

    iteration: int = Field(default=0, description="Current repair iteration counter.")
    max_iterations: int = Field(default=5, description="Maximum number of repair iterations before giving up.")

    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of code/test versions with failure summaries and fix rationales.",
    )

    def increment_iteration(self) -> None:
        self.iteration += 1

    def record_snapshot(self, **extra: Any) -> None:
        """Append a snapshot of the current state to history.

        Only stores lightweight metadata plus any provided extras, not entire large logs unless passed explicitly.
        """

        snapshot: Dict[str, Any] = {
            "iteration": self.iteration,
            "spec": self.spec,
            "has_code": self.code is not None,
            "has_tests": self.tests is not None,
        }
        snapshot.update(extra)
        self.history.append(snapshot)
