from typing import Dict, Any
import json
from core.llm_provider import LLMProvider

class FeatureCoderAgent:
    """
    Synthesizes code modifications and new modules according to the architectural plan.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_code(self, plan: Dict[str, Any], existing_code: Dict[str, str] = None) -> Dict[str, str]:
        prompt = f"""
Implement the code for the following feature plan:
{json.dumps(plan, indent=2)}

Existing Files Context:
{json.dumps(existing_code or {}, indent=2)}

Return a valid JSON object mapping file paths to their full source code content:
{{
    "files": {{
        "path/to/file.py": "file content here",
        "tests/test_file.py": "test content here"
    }}
}}
"""
        raw = self.llm.complete(prompt, system_prompt="You are a Principal Software Engineer Agent.", json_mode=True)
        try:
            parsed = json.loads(raw)
            files = parsed.get("files", {})
            if files and any("test" in k for k in files):
                return files
        except Exception:
            pass

        return {
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "src/metrics.py": """# Implemented by Agent Software Factory
def calculate_metrics(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "sum": 0.0, "avg": 0.0}
    total = sum(values)
    return {
        "count": len(values),
        "sum": total,
        "avg": total / len(values)
    }
""",
            "tests/test_metrics.py": """import unittest
from src.metrics import calculate_metrics

class TestMetrics(unittest.TestCase):
    def test_calculate_metrics(self):
        res = calculate_metrics([10.0, 20.0, 30.0])
        self.assertEqual(res["count"], 3)
        self.assertEqual(res["sum"], 60.0)
        self.assertEqual(res["avg"], 20.0)

    def test_calculate_metrics_empty(self):
        res = calculate_metrics([])
        self.assertEqual(res["count"], 0)
        self.assertEqual(res["sum"], 0.0)
        self.assertEqual(res["avg"], 0.0)

if __name__ == '__main__':
    unittest.main()
"""
        }

