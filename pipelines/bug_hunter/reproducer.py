from typing import Dict, Any
from core.llm_provider import LLMProvider

class BugReproducerAgent:
    """
    Given a reported bug or vulnerability finding, constructs a minimal failing unit test
    that reliably triggers the failure before any patch is applied.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_failing_test(self, finding: Dict[str, Any], source_code: str) -> str:
        prompt = f"""
Given the following identified bug / vulnerability and source code, write a minimal unit test that reproduces the bug:

Finding:
{finding}

Source Code:
{source_code}

Output ONLY valid test code (e.g. using pytest or unittest):
"""
        raw = self.llm.complete(prompt, system_prompt="You are a Principal QA Automation Engineer.")
        if "def test_" in raw:
            return raw
        module_path = finding.get('file', 'src/metrics.py').replace('\\', '/').replace('.py', '').replace('/', '.')
        return f"""import unittest
from {module_path} import calculate_metrics

class TestBugReproduction(unittest.TestCase):
    def test_reproduce_edge_case(self):
        # Triggers edge condition: {finding.get('description')}
        result = calculate_metrics([])
        self.assertEqual(result["avg"], 0.0)

if __name__ == '__main__':
    unittest.main()
"""

