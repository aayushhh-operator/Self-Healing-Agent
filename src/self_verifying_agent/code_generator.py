from __future__ import annotations

from .llm_factory import get_llm
from .state import AgentState
from .utils import strip_markdown


def generate_code(state: AgentState) -> AgentState:
    """Generate or regenerate implementation code from the parsed spec.

    For iteration 0, this creates an initial version. For later iterations, this may
    still be called but typically the code_fixer will handle modifications.
    """

    print(">>> Agent is generating the implementation code...")
    llm = get_llm()

    system = (
        "You are a senior Python engineer. Write minimal, readable, well-documented "
        "Python code implementing the requested function. Use only the standard library."
    )

    user = f"""
Parsed spec (JSON-like):
{state.parsed_spec}

Write a single Python module that:
- Defines exactly ONE top-level function matching the spec.
- Includes a clear docstring that restates the behavior and edge cases.
- Avoids overengineering; focus on correctness and clarity.
- Does not include any test code.
"""

    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    content = resp.content
    if isinstance(content, str):
        code = content
    else:
        # Concatenate parts if needed
        code = "".join(part["text"] for part in content if isinstance(part, dict) and "text" in part)

    state.code = strip_markdown(code)
    return state
