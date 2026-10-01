from typing import Dict, Any
from core.llm_provider import LLMProvider

class FeatureReviewerAgent:
    """
    Synthesizes git commit messages, PR descriptions, architectural impact summaries, and security audits.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def generate_pr_summary(self, plan: Dict[str, Any], files: Dict[str, str], test_results: Dict[str, Any]) -> str:
        prompt = f"""
Generate a professional GitHub Pull Request description based on the implemented feature and test validation:

Plan:
{plan}

Files Changed:
{list(files.keys())}

Test Execution Result:
Passed: {test_results.get('passed')}
Output: {test_results.get('stdout')}

Include:
- Summary of changes
- Architectural impact
- Testing & verification evidence
- Security considerations
"""
        return self.llm.complete(prompt, system_prompt="You are an Engineering Manager and Senior Code Reviewer.")
