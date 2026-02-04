from __future__ import annotations

from typing import Callable

from langgraph.graph import StateGraph, END

from .state import AgentState
from .spec_parser import parse_spec
from .code_generator import generate_code
from .test_generator import generate_tests
from .test_runner import run_tests
from .failure_analyzer import analyze_failures
from .code_fixer import fix_code


def build_graph() -> StateGraph:
    """Build the LangGraph workflow for the self-verifying code agent."""

    graph: StateGraph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("spec_parser", parse_spec)
    graph.add_node("code_generator", generate_code)
    graph.add_node("test_generator", generate_tests)
    graph.add_node("test_runner", run_tests)
    graph.add_node("failure_analyzer", analyze_failures)
    graph.add_node("code_fixer", fix_code)

    # Entry point
    graph.set_entry_point("spec_parser")

    # Linear path for first pass: parse -> code -> tests -> run -> analyze
    graph.add_edge("spec_parser", "code_generator")
    graph.add_edge("code_generator", "test_generator")
    graph.add_edge("test_generator", "test_runner")
    graph.add_edge("test_runner", "failure_analyzer")

    # Conditional edge from failure_analyzer: either stop or go to fixer.
    def route_after_analysis(state: AgentState) -> str:
        analysis = state.error_analysis or {}
        if analysis.get("status") == "success":
            return END
        if state.iteration >= state.max_iterations:
            return END
        # Otherwise, attempt a fix.
        return "code_fixer"

    graph.add_conditional_edges(
        "failure_analyzer",
        route_after_analysis,
        {"code_fixer": "code_fixer", END: END},
    )

    # After fixing code, rerun tests (but reuse tests).
    graph.add_edge("code_fixer", "test_runner")

    return graph


def run_self_verifying_agent(spec: str, max_iterations: int = 3) -> dict:
    """Run the self-verifying agent loop until tests pass or iterations exhausted."""

    initial_state = AgentState(spec=spec, max_iterations=max_iterations)

    graph = build_graph()
    app = graph.compile()

    # The graph itself handles the self-repair loop and iteration checking.
    # Streaming events to show progress in the terminal.
    final_state = {}
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            print(f"--- Running Node: {node_name} ---")
            final_state.update(state_update)

    return final_state


def stream_self_verifying_agent(spec: str, max_iterations: int = 3):
    """Streaming version of the self-verifying agent runner."""
    initial_state = AgentState(spec=spec, max_iterations=max_iterations)
    graph = build_graph()
    app = graph.compile()

    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            yield node_name, state_update
