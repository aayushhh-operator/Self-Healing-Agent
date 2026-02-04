from __future__ import annotations

import argparse
import json
import textwrap

from dotenv import load_dotenv

from self_verifying_agent.graph import run_self_verifying_agent

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the self-verifying code agent on a spec.")
    parser.add_argument("spec", nargs="?", help="Natural-language specification for the function.")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of self-repair iterations.",
    )

    args = parser.parse_args()

    if not args.spec:
        print("Please provide a spec, for example:")
        print(
            textwrap.dedent(
                """
                python -m examples.run_cli "Write a function that returns the k smallest pair sums from two sorted arrays."
                """
            ).strip()
        )
        raise SystemExit(1)

    print(f"Starting agent for spec: {args.spec}\n")
    
    final_state_data = run_self_verifying_agent(args.spec, max_iterations=args.max_iterations)

    print("\n=== Final Status ===")
    print(json.dumps(final_state_data.get("error_analysis"), indent=2, default=str))

    print("\n=== Final Code ===")
    print(final_state_data.get("code"))

    print("\n=== Tests ===")
    print(final_state_data.get("tests"))


if __name__ == "__main__":  # pragma: no cover
    main()
