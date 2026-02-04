from __future__ import annotations

from .llm_factory import get_llm
from .state import AgentState
from .utils import strip_markdown


def generate_tests(state: AgentState) -> AgentState:
    """Generate pytest-style unit tests based on the spec, not the implementation.

    Tests should cover happy paths, edge cases, and adversarial inputs and explain
    in comments why each test exists.
    """

    print(">>> Agent is generating unit tests...")
    llm = get_llm()

    system = (
        "You write focused pytest unit tests for a single Python function. "
        "You do NOT see the implementation, only the spec. Tests must be deterministic."
    )

    user = f"""
Original spec:
{state.spec}

Parsed spec:
{state.parsed_spec}

Write a pytest test module that:
- Imports the function from a module named `impl`.
- Contains tests grouped by scenario: happy path, edge cases, adversarial inputs.
- Uses clear test function names and comments explaining the purpose of each test.
- Uses only the Python standard library and pytest.
"""

    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    content = resp.content
    if isinstance(content, str):
        tests = content
    else:
        tests = "".join(part["text"] for part in content if isinstance(part, dict) and "text" in part)

    state.tests = strip_markdown(tests)
    return state
