from __future__ import annotations

from typing import Any, Dict

from .llm_factory import get_llm
from .state import AgentState
from .utils import strip_markdown


def parse_spec(state: AgentState) -> AgentState:
    """Parse the natural-language spec into a structured representation.

    Extracts function name, inputs, outputs, constraints, and edge cases.
    """

    print(">>> Agent is parsing the specification...")
    llm = get_llm()

    system = (
        "You parse natural-language programming specifications into a JSON schema. "
        "Extract function name, inputs (name + type + description), output, constraints, "
        "and explicit edge cases. Be concise and only return JSON."
    )

    user = f"""
Specification:
{state.spec}

Return JSON with keys: name, inputs, output, constraints, edge_cases, assumptions.
"""

    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    content = resp.content
    content = strip_markdown(content)
    if isinstance(content, str):
        # Best-effort parse, falling back to an empty dict if parsing fails.
        import json

        try:
            parsed: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"raw": content}
    else:
        parsed = {"raw": content}

    state.parsed_spec = parsed
    return state
