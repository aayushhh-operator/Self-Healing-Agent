from __future__ import annotations

from .llm_factory import get_llm
from .state import AgentState
from .utils import strip_markdown


def fix_code(state: AgentState) -> AgentState:
    """Modify the existing code based on error analysis.

    The model is instructed to make targeted edits instead of full rewrites where possible.
    """

    if state.code is None or state.error_analysis is None:
        return state

    print(f">>> Agent is attempting to fix the code (Iteration {state.iteration + 1})...")
    llm = get_llm()

    system = (
        "You are a careful Python refactoring assistant. Given code, a specification, "
        "and a description of failing tests, you make the smallest possible change to "
        "fix the bug while preserving style and structure. Return ONLY the updated code."
    )

    user = f"""
Specification:
{state.spec}

Current code:
{state.code}

Error analysis (JSON-like):
{state.error_analysis}

Raw test results (stdout):
{state.test_results.get("stdout") if state.test_results else "N/A"}

Raw test results (stderr):
{state.test_results.get("stderr") if state.test_results else "N/A"}

Update the code to address the described failures. Do not add unrelated features.
"""

    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    content = resp.content
    if isinstance(content, str):
        new_code = content
    else:
        new_code = "".join(part["text"] for part in content if isinstance(part, dict) and "text" in part)

    # Record a lightweight snapshot before overwriting.
    state.record_snapshot(
        event="fix_code",
        previous_error_analysis=state.error_analysis,
    )

    state.increment_iteration()
    state.code = strip_markdown(new_code)
    return state
