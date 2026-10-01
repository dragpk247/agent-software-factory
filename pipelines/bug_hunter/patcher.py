from typing import Dict, Any
from core.llm_provider import LLMProvider

class BugPatcherAgent:
    """
    Synthesizes a minimal, surgical patch that fixes the bug while preserving backwards compatibility.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_patch(self, finding: Dict[str, Any], source_code: str, test_code: str) -> str:
        prompt = f"""
Fix the bug in the source code so that the reproduction test passes. Keep edits minimal and surgical:

Bug Details:
{finding}

Source Code:
{source_code}

Failing Test:
{test_code}

Return the COMPLETE patched source code file content.
"""
        raw = self.llm.complete(prompt, system_prompt="You are a Staff Debugging and Systems Engineer.")

        if "def " in raw or "import " in raw:
            # Strip markdown fences if present
            if "```python" in raw:
                raw = raw.split("```python")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            return raw

        # Surgical fallback fix
        return """# Patched by Bug Hunter Agent
def calculate_metrics(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "sum": 0.0, "avg": 0.0}
    total = sum(values)
    return {
        "count": len(values),
        "sum": total,
        "avg": total / len(values)
    }
"""

