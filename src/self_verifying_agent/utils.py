import re

def strip_markdown(text: str) -> str:
    """Removes markdown code block delimiters from the start and end of a string."""
    # Matches ```python ... ``` or ```json ... ``` or just ``` ... ```
    pattern = r'^```(?:[a-zA-Z+]*)?\n?(.*?)\n?```$'
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return text.strip()
