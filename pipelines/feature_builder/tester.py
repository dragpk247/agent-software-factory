from typing import Tuple, Dict, Any
from core.sandbox import ExecutionSandbox

class FeatureTesterAgent:
    """
    Executes automated tests inside the isolated sandbox, analyzes compiler errors or test failures,
    and returns actionable feedback for self-healing loops.
    """
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox

    def run_tests(self, test_command: str = "python -m unittest discover tests") -> Dict[str, Any]:
        exit_code, stdout, stderr = self.sandbox.run_command(test_command)
        passed = (exit_code == 0)
        return {
            "passed": passed,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "feedback": None if passed else f"Test run failed with exit code {exit_code}.\nOutput: {stdout}\nErrors: {stderr}"
        }
