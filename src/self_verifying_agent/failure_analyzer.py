from __future__ import annotations

from typing import Any, Dict

from .llm_factory import get_llm
from .state import AgentState
from .utils import strip_markdown


def analyze_failures(state: AgentState) -> AgentState:
    """Analyze pytest output to explain failures and classify error types.

    If tests passed, marks the analysis accordingly.
    """

    results = state.test_results or {}
    exit_code = results.get("exit_code", 1)

    if exit_code == 0:
        state.error_analysis = {
            "status": "success",
            "summary": "All tests passed.",
        }
        return state

    print(">>> Agent is analyzing test failures...")
    llm = get_llm()

    system = (
        "You are an expert Python debugging assistant. Given pytest output, "
        "explain what failed, why it failed, and classify the error type as one of: "
        "logic_error, boundary_condition, performance_issue, type_mismatch, other. "
        "Reference specific lines from the traceback when possible. Return JSON only."
    )

    user = f"""
Specification:
{state.spec}

Code under test:
{state.code}

Tests:
{state.tests}

Pytest output (stdout):
{results.get("stdout", "")}

Pytest errors (stderr):
{results.get("stderr", "")}

Return JSON with keys: status, summary, error_type, focus_lines, suggestions.
"""

    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    content = resp.content
    content = strip_markdown(content)
    if isinstance(content, str):
        import json

        try:
            analysis: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            analysis = {"raw": content}
    else:
        analysis = {"raw": content}

    state.error_analysis = analysis
    return state
