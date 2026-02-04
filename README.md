# Self-Healing Agent

Self-Healing Agent is a self-verifying code generation system built with LangGraph and Groq. It takes natural language specifications, generates implementation code and unit tests, and iteratively repairs the code if tests fail.

## Features

- Specification Analysis: Parses natural language into structured requirements.
- Automated Code Generation: Creates Python implementation code based on the specification.
- Test Generation: Automatically generates pytest-style unit tests to verify the code.
- Self-Repair Loop: Runs tests and uses failure analysis to fix bugs automatically.
- Centralized LLM Management: Uses Groq (Llama 3.1) for high-performance inference.

## Project Structure

- `src/self_verifying_agent/`: Core agent logic and Graph definition.
- `examples/`: Example scripts to run the agent.
- `requirements.txt`: Project dependencies.
- `pyproject.toml`: Package configuration.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file in the root directory and add your Groq API key:
   ```text
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

You can run the agent using the provided CLI example:

```bash
python -m examples.run_cli "Write a function that returns whether or not a given number is prime"
```

### Options

- `spec`: The natural language specification for the function.
- `--max-iterations`: Maximum number of self-repair attempts (default: 3).

## Workflow

The agent follows a graph-based workflow:

1. spec_parser: Converts the prompt into a JSON schema.
2. code_generator: Writes the initial implementation.
3. test_generator: Writes pytest-compatible unit tests.
4. test_runner: Executes the generated tests.
5. failure_analyzer: (If tests fail) Analyzes tracebacks to identify root causes.
6. code_fixer: (If tests fail) Modifies the code based on the analysis and repeats from step 4.
